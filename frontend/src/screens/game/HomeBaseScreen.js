// HomeBase Screen - starting screen for player to manage their party and enter the dungeon
// The only way to enter the dungeon
// 

import React, { useState, useEffect, useCallback } from "react";
import PartyDisplay from "../../components/cardDisplays/PartyDisplay";
import MonsterPoolDisplay from "../../components/cardDisplays/MonsterPoolDisplay";
import { useEnterDungeon } from "../../app/hooks/useDungeon";
import { Card, CardSection, Button } from "../../shared/ui";

function HomeBaseScreen(){

    const {
        isLoading,
        enterDungeon
    } = useEnterDungeon();

    const handleEnterDungeon = useCallback(async () => {
        await enterDungeon();
    }, [enterDungeon]);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <Card size="xl" background="light" >
                <CardSection type="header" size="xl" title="🏠 Home Base" alignment="center">
                    <p>Prepare your party and venture into the unknown dungeons.</p>
                </CardSection>
                <CardSection type="content" alignment="center" background="light">
                    <Button 
                        size="xl" 
                        icon="🏰"
                        onClick={handleEnterDungeon}
                        disabled={isLoading}
                    >
                            Enter the dungeon
                    </Button>
                </CardSection>
            </Card>

            <PartyDisplay/>
            
            <MonsterPoolDisplay />
        </div>
    )
}

export default HomeBaseScreen;