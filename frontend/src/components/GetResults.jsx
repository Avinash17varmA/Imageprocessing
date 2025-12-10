import API from "../api/client";
import { useState } from "react";
import JSZip from "jszip";

export default function GetResults(props) {
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState([]);

  const fetchResults = async () => {
    setLoading(true);
    setImages([]);

    try {
      const res = await API.get("/backend/raw-images/", {
        responseType: "arraybuffer", // IMPORTANT
      });

      const zip = await JSZip.loadAsync(res.data);
      const extractedImages = [];

      for (const filename of Object.keys(zip.files)) {
        const file = zip.files[filename];

        // skip folders
        if (file.dir) continue;

        // convert each image into a Blob → url for <img>
        const blob = await file.async("blob");
        const url = URL.createObjectURL(blob);

        extractedImages.push({ name: filename, url });
      }

      setImages(extractedImages);
    } catch (error) {
      console.error(error);
      alert("Failed to load images");
    }

    setLoading(false);
  };

  return (
    <div className="card">
      <div className="flex" style={{ justifyContent: "space-between", marginBottom: "1.5rem" }}>
        <h2 style={{ margin: 0 }}>Processing History</h2>
        <button onClick={fetchResults} disabled={loading} style={{ minWidth: "120px" }}>
          {loading ? "Fetching..." : "Refresh History"}
        </button>
      </div>

      <div className="grid">
        {images.length > 0 ? (
          images.map((img, idx) => (
            <div
              key={idx}
              style={{
                backgroundColor: "var(--bg-input)",
                padding: "10px",
                borderRadius: "var(--radius)",
                border: "1px solid var(--border)",
                transition: "transform 0.2s",
                cursor: "zoom-in"
              }}
              onClick={() => props.onImageClick && props.onImageClick({ src: img.url, alt: img.name })}
              onMouseOver={(e) => e.currentTarget.style.transform = "translateY(-4px)"}
              onMouseOut={(e) => e.currentTarget.style.transform = "none"}
            >
              <div style={{ marginBottom: "0.5rem", fontSize: "0.9rem", color: "var(--text-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {img.name}
              </div>
              <img
                src={img.url}
                alt={img.name}
                style={{ width: "100%", borderRadius: "8px", display: "block", aspectRatio: "16/9", objectFit: "cover" }}
              />
            </div>
          ))
        ) : (
          <div style={{ gridColumn: "1 / -1", textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
            {!loading && "No history available. Upload an image to start."}
          </div>
        )}
      </div>
    </div>
  );
}
