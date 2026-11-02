// Offline synthetic behavior checks; no connection URL or service credentials accepted.
import assert from 'node:assert/strict';
import path from 'node:path';
import {createRequire} from 'node:module';
import {rehearse} from '../skills/minwoo-postgres-review/scripts/rehearse.mjs';

if (process.argv.length !== 3) throw Error('Usage: node evals/verify_db_safety.mjs <installed-kit-runtime>');
const runtime = path.resolve(process.argv[2]);
const require = createRequire(path.join(runtime, 'package.json'));
const {PGlite} = require('@electric-sql/pglite');
const results = [];
async function check(name, fn) {
  try { await fn(); results.push({name, passed: true}); }
  catch (e) { results.push({name, passed: false, error: e.code || e.name}); }
}
const setup = "CREATE TABLE items(id integer PRIMARY KEY, name text NOT NULL); INSERT INTO items VALUES(1,'one'),(2,'two');";
const up = 'ALTER TABLE items ADD COLUMN enabled boolean NOT NULL DEFAULT true;';
const down = 'ALTER TABLE items DROP COLUMN enabled;';
const checks = {
  before: [{sql: 'SELECT id,name FROM items ORDER BY id', rows: [{id:1,name:'one'},{id:2,name:'two'}]}],
  after: [{sql: 'SELECT id,name,enabled FROM items ORDER BY id', rows: [{id:1,name:'one',enabled:true},{id:2,name:'two',enabled:true}]}]
};
await check('migration-preserves-values-and-down', async () => {
  const r = await rehearse({runtime, setup, up, down, checks});
  assert.equal(r.passed, true);
  assert.equal(r.rollback, 'verified against before assertions');
});
await check('same-row-count-value-loss-detected', async () => {
  const r = await rehearse({runtime, setup, up: up + " UPDATE items SET name='lost';", down, checks});
  assert.equal(r.passed, false); assert.equal(r.failed_stage, 'after');
});
await check('incorrect-down-detected', async () => {
  const r = await rehearse({runtime, setup, up, down: down + " UPDATE items SET name='lost';", checks});
  assert.equal(r.passed, false); assert.equal(r.failed_stage, 'restored');
});
await check('missing-down-not-claimed-as-recovery', async () => {
  const r = await rehearse({runtime, setup, up, checks});
  assert.equal(r.passed, true); assert.equal(r.rollback, 'not tested');
});
const db = new PGlite();
let restored;
let engine;
async function asRole(role, fn, target = db) {
  // Only literal roles from this fixture, never user-controlled SQL.
  assert(['tenant_a','tenant_b','audit_reader','fixture_owner'].includes(role));
  await target.exec('SET ROLE ' + role);
  try { await fn(target); } finally { await target.exec('RESET ROLE'); }
}
async function denied(target, sql, code = '42501') {
  await assert.rejects(target.query(sql), e => e.code === code);
}
try {
  await db.exec(`
    CREATE ROLE fixture_owner NOLOGIN NOSUPERUSER NOBYPASSRLS;
    CREATE ROLE tenant_a NOLOGIN NOSUPERUSER NOBYPASSRLS;
    CREATE ROLE tenant_b NOLOGIN NOSUPERUSER NOBYPASSRLS;
    CREATE ROLE audit_reader NOLOGIN NOSUPERUSER NOBYPASSRLS;
    CREATE SCHEMA fixture AUTHORIZATION fixture_owner;
    CREATE TABLE fixture.notes(id integer PRIMARY KEY, tenant text NOT NULL, body text NOT NULL CHECK(body <> ''));
    ALTER TABLE fixture.notes OWNER TO fixture_owner;
    INSERT INTO fixture.notes VALUES(1,'tenant_a','alpha'),(2,'tenant_b','beta');
    ALTER TABLE fixture.notes ENABLE ROW LEVEL SECURITY;
    CREATE POLICY own_rows ON fixture.notes TO tenant_a, tenant_b
      USING(tenant = current_user) WITH CHECK(tenant = current_user);
    CREATE POLICY audit_rows ON fixture.notes FOR SELECT TO audit_reader USING(true);
    GRANT USAGE ON SCHEMA fixture TO tenant_a, tenant_b, audit_reader;
    GRANT SELECT,INSERT,UPDATE,DELETE ON fixture.notes TO tenant_a,tenant_b;
    GRANT SELECT ON fixture.notes TO audit_reader;
  `);
  engine = (await db.query('SHOW server_version')).rows[0].server_version;
  await check('rls-actual-roles-own-vs-other-rows', async () => {
    for (const [role,id] of [['tenant_a',1],['tenant_b',2]]) {
      await asRole(role, async target => {
        const identity = (await target.query('SELECT current_user AS role')).rows[0];
        assert.equal(identity.role, role);
        assert.deepEqual((await target.query('SELECT id FROM fixture.notes ORDER BY id')).rows, [{id}]);
      });
    }
  });
  await check('rls-cross-tenant-update-zero-rows', async () => {
    await asRole('tenant_a', async target => {
      assert.deepEqual((await target.query("UPDATE fixture.notes SET body='bad' WHERE id=2 RETURNING id")).rows, []);
    });
    assert.deepEqual((await db.query('SELECT body FROM fixture.notes WHERE id=2')).rows,[{body:'beta'}]);
  });
  await check('rls-insert-and-owner-change-denied', async () => {
    await asRole('tenant_a', async target => {
      await denied(target, "INSERT INTO fixture.notes VALUES(3,'tenant_b','bad')");
      await denied(target, "UPDATE fixture.notes SET tenant='tenant_b' WHERE id=1");
    });
  });
  await check('rls-permitted-write-succeeds', async () => {
    await asRole('tenant_a', async target => {
      assert.deepEqual((await target.query("UPDATE fixture.notes SET body='allowed' WHERE id=1 RETURNING id")).rows,[{id:1}]);
    });
    assert.deepEqual((await db.query('SELECT body FROM fixture.notes WHERE id=1')).rows,[{body:'allowed'}]);
  });
  await check('readonly-role-select-allowed-writes-and-ddl-denied', async () => {
    await asRole('audit_reader', async target => {
      assert.equal((await target.query('SELECT * FROM fixture.notes')).rows.length,2);
      for (const sql of ["UPDATE fixture.notes SET body='bad'","DELETE FROM fixture.notes","TRUNCATE fixture.notes","ALTER TABLE fixture.notes ADD COLUMN bad integer"]) {
        await denied(target,sql);
      }
    });
  });
  await check('owner-bypasses-rls-invalid-test-role', async () => {
    await asRole('fixture_owner', async target => {
      assert.equal((await target.query('SELECT * FROM fixture.notes')).rows.length,2);
    });
  });
  await check('readonly-transaction-blocks-write', async () => {
    await db.exec('BEGIN READ ONLY');
    try { await denied(db,"UPDATE fixture.notes SET body='bad'",'25006'); }
    finally { await db.exec('ROLLBACK'); }
  });
  await check('snapshot-restores-values-constraints-and-role-policy', async () => {
    const expected = (await db.query('SELECT * FROM fixture.notes ORDER BY id')).rows;
    const snapshot = await db.dumpDataDir();
    assert(snapshot.size > 0);
    await db.exec("UPDATE fixture.notes SET body='damaged'");
    restored = new PGlite({loadDataDir: snapshot});
    assert.deepEqual((await restored.query('SELECT * FROM fixture.notes ORDER BY id')).rows,expected);
    await denied(restored,"INSERT INTO fixture.notes VALUES(1,'tenant_a','duplicate')",'23505');
    await denied(restored,"INSERT INTO fixture.notes VALUES(3,'tenant_a','')",'23514');
    await asRole('tenant_a', async target => {
      assert.deepEqual((await target.query('SELECT id FROM fixture.notes')).rows,[{id:1}]);
      await denied(target,"UPDATE fixture.notes SET tenant='tenant_b' WHERE id=1");
    }, restored);
    await asRole('audit_reader', target => denied(target,'TRUNCATE fixture.notes'), restored);
  });
} finally {
  if (restored) await restored.close();
  await db.close();
}
const report = {
  scope: 'Synthetic in-memory PGlite only; no cloud DB, credentials, network, native pg_dump/PITR or model selection test',
  node: process.version, postgres: engine, cases: results.length,
  passed: results.filter(r => r.passed).length, results
};
console.log(JSON.stringify(report,null,2));
process.exitCode = results.every(r => r.passed) ? 0 : 1;
