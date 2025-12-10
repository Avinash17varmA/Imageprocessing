import React, { useState } from "react";
import axios from "axios";
import JSZip from "jszip";

function UploadForm(props) {
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
    <div className="card">
      <h2 className="mb-4">Upload Image</h2>

      <div className="flex" style={{ flexDirection: "column", alignItems: "start", gap: "1rem" }}>
        <div style={{ width: "100%" }}>
          <label
            htmlFor="file-upload"
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              border: "2px dashed var(--border)",
              borderRadius: "var(--radius)",
              padding: "3rem",
              textAlign: "center",
              cursor: "pointer",
              color: "var(--text-muted)",
              transition: "all 0.2s",
              backgroundColor: "rgba(255, 255, 255, 0.02)"
            }}
            onDragOver={(e) => {
              e.preventDefault();
              e.currentTarget.style.borderColor = "var(--primary)";
              e.currentTarget.style.backgroundColor = "rgba(139, 92, 246, 0.1)";
            }}
            onDragLeave={(e) => {
              e.preventDefault();
              e.currentTarget.style.borderColor = "var(--border)";
              e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.02)";
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.currentTarget.style.borderColor = "var(--border)";
              e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.02)";
              if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                setFile(e.dataTransfer.files[0]);
                setStatus("");
                setImages([]);
              }
            }}
            onMouseOver={(e) => e.currentTarget.style.borderColor = "var(--primary)"}
            onMouseOut={(e) => e.currentTarget.style.borderColor = "var(--border)"}
          >
            <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>📂</div>
            {file ? (
              <span style={{ color: "var(--text-main)", fontWeight: "500" }}>{file.name}</span>
            ) : (
              <span>Click to select or drag & drop an image</span>
            )}
          </label>
          <input
            id="file-upload"
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
        </div>

        <div className="flex" style={{ width: "100%", justifyContent: "space-between" }}>
          <button onClick={handleUpload} disabled={!file || status === "Uploading..."}>
            {status === "Uploading..." ? "Uploading..." : "Process Image"}
          </button>

          {status && (
            <span style={{
              color: status.includes("Error") ? "#ff6b6b" : "var(--primary)",
              fontWeight: "500"
            }}>
              {status}
            </span>
          )}
        </div>
      </div>

      {images.length > 0 && (
        <div className="mt-4">
          <h3 className="mb-4">Processed Results</h3>
          <div className="grid">
            {images.map((img, index) => (
              <div
                key={index}
                style={{
                  backgroundColor: "var(--bg-input)",
                  padding: "10px",
                  borderRadius: "var(--radius)",
                  border: "1px solid var(--border)",
                  cursor: "zoom-in",
                  transition: "transform 0.2s"
                }}
                onClick={() => props.onImageClick && props.onImageClick({ src: img.data, alt: img.name })}
                onMouseOver={(e) => e.currentTarget.style.transform = "translateY(-4px)"}
                onMouseOut={(e) => e.currentTarget.style.transform = "none"}
              >
                <div style={{ marginBottom: "0.5rem", fontSize: "0.9rem", color: "var(--text-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {img.name}
                </div>
                <img
                  src={img.data}
                  alt={img.name}
                  style={{ width: "100%", borderRadius: "8px", display: "block" }}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default UploadForm;
