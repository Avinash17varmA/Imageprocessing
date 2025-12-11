import axios from "axios";
import JSZip from "jszip";

const API = axios.create({
  baseURL: "http://localhost:8000",
  responseType: "blob",
});

export const processZipResponse = async (data) => {
  const zip = await JSZip.loadAsync(data);
  const extractedImages = [];

  for (const filename of Object.keys(zip.files)) {
    // Skip directories
    if (zip.files[filename].dir) continue;

    const fileData = await zip.files[filename].async("base64");
    extractedImages.push({
      name: filename,
      data: `data:image/png;base64,${fileData}`,
    });
  }
  return extractedImages;
};

export default API;
