import React from "react";
import SequentialModel from "../../assets/model_assets/SEA_CHANGE_TEST1.mo?url";
import uploadModel from "../funtion_utils/ModelSelectorUtils";
const ModelSelector = () =>{
    /**
     * UpLoad the modelcia mdoel to the backend
     */
    async function handleLoadModel(){
        uploadModel(SequentialModel)
    }
    return (
        <>
            <div> 
                <button onClick ={handleLoadModel}> Load Sequential Model</button>
            </div>
        </>
    )
}
export default ModelSelector