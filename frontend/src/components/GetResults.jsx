import API from "../api/client";
import { useState } from "react";
import JSZip from "jszip";

export default function GetResults() {
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
    <div className="results-box">
      <h2>Existing Data</h2>

      <button onClick={fetchResults} disabled={loading}>
        {loading ? "Fetching..." : "History"}
      </button>

      <div className="image-gallery" style={{ marginTop: "20px" }}>
        {images.length > 0 &&
          images.map((img, idx) => (
            <div key={idx} style={{ marginBottom: "10px" }}>
              <p>{img.name}</p>
              <img
                src={img.url}
                alt={img.name}
                style={{ width: "200px", borderRadius: "8px" }}
              />
            </div>
          ))}
      </div>
    </div>
  );
}
