const uploadModel = async (url)=>{
    let modelName;
    try{
        //Fetch modelica file as a text 
        const res = await fetch (url);
        const text = await res.text();
        const filePath = url;
        const modelBase64File = textToBase64(text);
        const fileName = filePath.split("/").pop();
        modelName = fileName.replace(/\.[^/.]+$/, ""); 

        // Upload to backend
        const response = await fetch("http://127.0.0.1:5000/seq_model/upload", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                model_name: modelName,
                model_data: modelBase64File,
            }),
        });
        console.log(`Uploading: ${modelName}`)
        const data = await response.json();
        if (data.status === "Model written") {
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

function textToBase64(text) {
  // Encode to UTF-8, then to base64
  return window.btoa(unescape(encodeURIComponent(text)));
}