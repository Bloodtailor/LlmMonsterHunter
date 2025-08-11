// DeveloperScreen 
// 
// 

import AiLogTableContainer from '../../components/developer/AiLogTable/AiLogTableContainer.js';
import TestRunner from '../../components/developer/GameTestRunner/GameTestRunner.js';
import { Card, CardSection } from '../../shared/ui/index.js';

function DeveloperScreen() {
  return (
    <div 
    style={{display: 'flex', flexDirection:'column', gap:'24px'}}
    >
      {/* Header */}
      <Card  background='light' size='xl' >
        <CardSection type="header" title="Developer Screen" alignment='center'>
          <p >
            Monitor LLM and Image generation logs with expandable details. 
            Run backend tests
          </p>
        </CardSection>
      </Card>

      <TestRunner/>

      {/* Main Log Table */}
      <AiLogTableContainer />
    </div>
  );
}

export default DeveloperScreen;