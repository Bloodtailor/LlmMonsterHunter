import React, { useState, useCallback, useRef, useMemo } from "react";
import { useApi } from "../../refactored/shared/hooks/useApi";
import { getMonsterTemplates, getMonster } from "../../refactored/api/services/monsters";

function MyCurrentTestScreen() {
    const [input, setInput] = useState(1);
    const [monsterId, setMonsterId] = useState(1);
    const {
        data: templateData, 
        execute: templateExecute, 
        isLoading: templateIsLoading, 
        isError: templateIsError
    } = useApi(getMonsterTemplates, {immediate: false});
    const {
        data: monsterData,
        execute: monsterExecute,
        isLoading: monsterIsLoading,
        isError: monsterIsError
    } =  useApi(getMonster, {immediate: false});

    const handleInputChange = (e) => {
        setInput(e.target.value);
    };

    const handleButton = useCallback(() => {
        monsterExecute(input);
    }, [input]);


    return (
        <div>
            <div>
                <button onClick={templateExecute}>Get Monster Templates</button>
                {templateIsLoading && <p>Loading...</p>}
                {templateIsError && <p>Error fetching data</p>}
                {templateData && !templateIsLoading && <pre>{JSON.stringify(templateData, null, 2)}</pre>}
            </div>

            <div>
                <input type="number" value={input} onChange={handleInputChange}/> 
                <button onClick={handleButton}>Get monster</button>
                {monsterIsLoading && <p>Loading...</p>}
                {monsterIsError && <p>Error fetching data</p>}
                {monsterData && !monsterIsLoading && <p>{JSON.stringify(monsterData, null, 2)}</p>}
                {input && !monsterIsLoading && <p>{JSON.stringify(input, null, 2)}</p>}
                {monsterId && !monsterIsLoading && <p>{JSON.stringify(monsterId, null, 2)}</p>}
            </div>

        </div>
    );
}

export default MyCurrentTestScreen;
