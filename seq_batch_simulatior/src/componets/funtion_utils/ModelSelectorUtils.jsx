const uploadModel = async (url)=>{
    let modelName;
    try{
        //Fetch modelica file as a text 
        const res = await fetch (url);
        const text = await res.text();
        const filePath = url;
        const modelBase64File = btoa(text);
        const fileName = filePath.split("/").pop();
        modelName = fileName.replace(/\.[^/.]+$/, ""); 
        // Upload to backend
        const response = await axios.post("http://127.0.0.1:5000/model/upload", {
            model_name: modelName,
            model_data: modelBase64File,
        });
        console.log("Uploading")
        if (response.data.status === "Model written") {
            console.log("Loading successful");
        } else {
            console.log("Model Not Written");
            alert("Model Not Written");
        }
    }catch(e){
        console.error(e);
        alert("Model Uploading Failed");
    }
}
export default uploadModel;