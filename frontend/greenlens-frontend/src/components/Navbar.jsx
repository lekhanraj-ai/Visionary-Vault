import { Link } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="logo">🌱 GreenLens</div>
      <ul>
        <li><Link to="/">Dashboard</Link></li>
        <li><Link to="/chat">Ask ESG</Link></li>
        <li><Link to="/upload">Upload Docs</Link></li>
      </ul>
    </nav>
  );
}
