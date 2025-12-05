import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000", // your Django backend
  responseType: "blob",  // because backend returns ZIP files
});

export default API;
