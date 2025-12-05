import React, { useState } from "react";
import axios from "axios";
import JSZip from "jszip";

function UploadForm() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [images, setImages] = useState([]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatus("");
    setImages([]);
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus("Please select an image first.");
      return;
    }

    try {
      setStatus("Uploading...");

      const formData = new FormData();
      formData.append("file", file);

      const response = await axios.post(
        "http://localhost:8000/backend/upload-image/",
        formData,
        {
          responseType: "arraybuffer", // ZIP file comes as binary
        }
      );

      setStatus("Processing ZIP...");

      const zip = await JSZip.loadAsync(response.data);
      const extractedImages = [];

      // Loop through each file in the ZIP
      for (const filename of Object.keys(zip.files)) {
        const fileData = await zip.files[filename].async("base64");
        extractedImages.push({
          name: filename,
          data: `data:image/png;base64,${fileData}`,
        });
      }

      setImages(extractedImages);
      setStatus("Completed!");

    } catch (error) {
      console.error(error);
      setStatus("Error uploading or processing ZIP.");
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>Upload Image for Processing</h1>

      <input type="file" accept="image/*" onChange={handleFileChange} />
      <br /> <br />

      <button
        onClick={handleUpload}
        style={{ padding: "10px 20px", cursor: "pointer" }}
      >
        Upload
      </button>

      <p style={{ marginTop: "10px" }}>{status}</p>

      <div
        style={{
          marginTop: "20px",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
          gap: "20px",
        }}
      >
        {images.map((img, index) => (
          <div
            key={index}
            style={{
              border: "1px solid #ddd",
              padding: "10px",
              borderRadius: "8px",
            }}
          >
            <h4 style={{ fontSize: "14px" }}>{img.name}</h4>
            <img
              src={img.data}
              alt={img.name}
              style={{ width: "100%", borderRadius: "6px" }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export default UploadForm;
