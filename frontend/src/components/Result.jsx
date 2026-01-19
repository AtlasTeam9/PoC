import React from 'react';
import { useState } from 'react';

function Result({requirement, result}){

    const getColor = () => {
        if (result === "PASS") return 'green';
        if (result === "FAIL") return 'red';
        if (result === "NOT_APPLICABLE") return 'orange';
        return 'gray';
    };

    return (
        <>  
            <div style={{color : 'gray', margin:'5px 0px'}}>
                <div style={{backgroundColor:'white',padding:'15px',display:'flex',flexDirection:'row',justifyContent:'space-between',alignItems:'center'}}>
                    <span style={{fontSize:'16px'}}>{requirement}</span>
                    <span style={{color:getColor(),fontSize:'18px',fontWeight:'bold'}}>
                        {result == "NOT_APPLICABLE" ? "NA" : result}
                    </span>
                </div>
            </div>
        </>
    )
}

export default Result