import React from 'react';
import {AbsoluteFill, Composition, registerRoot, useCurrentFrame, useVideoConfig} from 'remotion';
import {parseSrt} from '@remotion/captions';

const {captions} = parseSrt({input: '1\n00:00:00,300 --> 00:00:00,900\n첫 번째 자막\n\n2\n00:00:01,200 --> 00:00:01,800\n두 번째 자막\n'});
function Sample() {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ms = frame / fps * 1000;
  const caption = captions.find(c => c.startMs <= ms && ms < c.endMs);
  return <AbsoluteFill style={{background:'#102338',color:'#fff',fontFamily:'Malgun Gothic, sans-serif',
    alignItems:'center',justifyContent:'center',fontSize:34}}>
    <div style={{fontSize:16,color:'#9ecde8',marginBottom:30}}>Codex kit · render check</div>
    <div>{caption?.text ?? '자막 사이 빈 구간'}</div>
    <div style={{fontSize:16,marginTop:28}}>frame {frame}</div>
  </AbsoluteFill>;
}
function Root() {
  return <Composition id="CaptionCheck" component={Sample} width={640} height={360}
    fps={30} durationInFrames={60}/>;
}
registerRoot(Root);
