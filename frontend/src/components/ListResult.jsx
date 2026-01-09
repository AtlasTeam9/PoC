import React from 'react';
import { useState } from 'react';
import Result from './Result'

function ListResult({asset_name, data}){
    const [ isShowed, showResults ] = useState(false)

    const showList = () => {
        showResults(!isShowed)
    }   

    return (
        <>  
            <div style={{color : 'gray', margin:'5px 0px'}}>
                <span style={{fontSize:'20px', cursor:'pointer'}} onClick={showList}>{asset_name}</span>
                {
                isShowed && Object.entries(data[0]).map(([requirement, result]) => (
                    <Result requirement={requirement} result={result.status} />
                ))
                }
            </div>
        </>
    )
}

export default ListResult