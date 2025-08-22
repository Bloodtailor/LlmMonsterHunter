// HomeBase Screen - starting screen for player to manage their party and enter the dungeon
// Now uses NavigationContext to navigate to dungeon screens
// The only way to enter the dungeon

import React from 'react';
import PartyDisplay from "../../components/cardDisplays/PartyDisplay";
import MonsterPoolDisplay from "../../components/cardDisplays/MonsterPoolDisplay";
import { Card, CardSection, Button } from "../../shared/ui";
import { useNavigation } from "../../app/contexts/NavigationContext/index.js";

function HomeBaseScreen() {
    const { navigateToGameScreen } = useNavigation();

    const handleEnterDungeon = () => {
        navigateToGameScreen('dungeon-entrance');
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <Card size="xl" background="light">
                <CardSection type="header" size="xl" title="🏠 Home Base" alignment="center">
                    <p>Prepare your party and venture into the unknown dungeons.</p>
                </CardSection>
                <CardSection type="content" alignment="center" background="light">
                    <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', justifyContent: 'center' }}>
                        <Button 
                            size="xl" 
                            icon="🏰"
                            onClick={handleEnterDungeon}
                        >
                            Enter the dungeon
                        </Button>
                        
                        <Button 
                            size="xl" 
                            icon="🏛️"
                            variant="secondary"
                            onClick={() => navigateToGameScreen('sanctuary')}
                        >
                            Monster Sanctuary
                        </Button>
                    </div>
                </CardSection>
            </Card>

            <PartyDisplay />
            
            <MonsterPoolDisplay />
        </div>
    );
}

export default HomeBaseScreen;