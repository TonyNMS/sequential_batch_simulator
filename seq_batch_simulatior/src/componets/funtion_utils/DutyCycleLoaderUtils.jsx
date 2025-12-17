
export async function savingFile(){
    /**
     * Saving file to the /assets/duty_cycle
     * Return the file name and file absolute URL 
     */
    let success = true
    let file_name = ""
    let file_path = ""
    
    return {
        "saving_status" : success,
        "file_name" : file_name,
        "file_path" : file_path
    }
}