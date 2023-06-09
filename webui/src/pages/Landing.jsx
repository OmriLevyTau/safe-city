import { useNavigate } from "react-router-dom";
import bgImage from "./background3.png";
import logo from "./logo.png"

const bgColor = "#252525";
const titleColor = "#967E76";
const bodyColor = "#D7C0AE";
const fontFamily = "Geologica";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        backgroundColor: bgColor,
        fontFamily: fontFamily,
        height: "100vh", 
      }}
    >
      <div style={{ flex: 0.7,}}>
      <img src={logo} style={{ display: "block", margin: "0 auto" }} />
        <div style={{ textAlign: "center", color: titleColor, marginTop: "5%" }}>
          <h1 style={{ fontSize: `max(24px, 3vw)` }}>Tel-Aviv is Safe City</h1>
        </div>

        <div
          style={{
            textAlign: "center",
            color: bodyColor,
            letterSpacing: "2px",
            fontWeight: "450",
            marginTop: "5%",
            marginBottom: "8%",
          }}
        >
          <h3 style={{ lineHeight: 1.5 , fontSize: "2.4rem"}}>

            Stride with Confidence: Your Guide to Safer Walks<br />

          </h3>
        </div>

        <div style={{ textAlign: "center" }}>
          <button
            size="large"
            shape="round"
            color="#967E76"
            onClick={() => navigate("/home")}
            style={{
              borderRadius: "10px",
              width: "200px",
              height: "50px",
              fontFamily: fontFamily,
              fontSize: "2rem",
              backgroundColor: "#EEE3CB",
              transition: "background-color 0.3s ease",
            }}
          >
            Get Started!
          </button>
        </div>
      </div>

      <div style={{ flex: 1, height:"100%" }}>
        <img src={bgImage} alt="Background" style={{ width: "100%", height:"100%" }} />
      </div>
    </div>
  );
}
