import React, { useContext, useState } from "react";
import { DutyCycleContext } from "../../App";
const DutyCycleLoader = () => {
  const [fileName, setFileName] = useState("");
  const [filePath, setFilePath] = useState("");
  const [startTime, setStartTime] = useState(null);
  const [endTime, setEndTime] = useState(null);
  const [maxPower, setMaxPower] = useState(null);
  const [status, setStatus] = useState("");
  const [dutycyleObj, setDutyCycleObj] = useContext(DutyCycleContext)
  const handleFileInput = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileName(file.name);
    setStatus("Uploading...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:5000/seq_model/upload_dutyCycle", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok || !data.status) {
        throw new Error(data.reason || "Upload failed");
      }

      setFilePath(data.file_path);
      setStartTime(data.startTime);
      setEndTime(data.endTime);
      setMaxPower(data.maxPower);
      setStatus("Upload successful");
      const dutycycleInfo ={
        "startTime" : data.startTime,
        "endTime" : data.endTime,
        "maxPower" : data.maxPower,
        "dutyCyclePath":data.file_path
      }
      setDutyCycleObj(dutycycleInfo)
    } catch (err) {
      console.error(err);
      setStatus("Upload failed");
    }
  };

  return (
    <div style={{ padding: "1rem" }}>
      <input type="file" accept=".txt" onChange={handleFileInput} />

      {status && <p>{status}</p>}

      {filePath && (
        <div>
          <p><strong>File:</strong> {fileName}</p>
          <p><strong>Path:</strong> {filePath}</p>
          <p><strong>Start Time:</strong> {startTime}</p>
          <p><strong>End Time:</strong> {endTime}</p>
          <p><strong>Max Power:</strong> {maxPower}</p>
        </div>
      )}
    </div>
  );
};

export default DutyCycleLoader;
