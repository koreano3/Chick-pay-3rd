import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

// 페이지 컴포넌트들
import Login from "./pages/Login";
import Register from "./pages/Register";
import Main from "./pages/Main";
import MyPage from "./pages/MyPage";
import Deposit from "./pages/Deposit";
import DepositComplete from "./pages/DepositComplete";
import Withdraw from "./pages/Withdraw";
import Transfer from "./pages/Transfer";
import OTPSetup from "./pages/OTPSetup";
import Unregister from "./pages/Unregister";
import PrivateRoute from "./components/PrivateRoute";
import WithdrawComplete from "./pages/WithdrawComplete";

// 테마 설정
const theme = createTheme({
  palette: {
    primary: {
      main: "#FFDE59", // chick-yellow
    },
    secondary: {
      main: "#FFC93C", // chick-orange
    },
    background: {
      default: "#FFF9E5", // chick-light
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/mypage" element={<MyPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/unregister"
            element={
              <PrivateRoute>
                <Unregister />
              </PrivateRoute>
            }
          />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Main />
              </PrivateRoute>
            }
          />
          <Route
            path="/deposit"
            element={
              <PrivateRoute>
                <Deposit />
              </PrivateRoute>
            }
          />
          <Route
            path="/deposit/complete"
            element={
              <PrivateRoute>
                <DepositComplete />
              </PrivateRoute>
            }
          />
          <Route
            path="/withdraw"
            element={
              <PrivateRoute>
                <Withdraw />
              </PrivateRoute>
            }
          />
          <Route
            path="/withdraw-complete"
            element={
              <PrivateRoute>
                <WithdrawComplete />
              </PrivateRoute>
            }
          />
          <Route
            path="/transfer"
            element={
              <PrivateRoute>
                <Transfer />
              </PrivateRoute>
            }
          />
          <Route
            path="/otp-setup"
            element={
              <PrivateRoute>
                <OTPSetup />
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
