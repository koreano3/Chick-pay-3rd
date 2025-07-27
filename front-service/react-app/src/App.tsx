import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

// 페이지 컴포넌트들
import Login from "./pages/Login";
import Register from "./pages/Register";
import Main from "./pages/Main";
import MyPage from "./pages/MyPage";
// import Account from "./pages/Account";
import Deposit from "./pages/Deposit";
import DepositComplete from "./pages/DepositComplete";
import Withdraw from "./pages/Withdraw";
import WithdrawComplete from "./pages/WithdrawComplete";
import Transfer from "./pages/Transfer";
import TransferComplete from "./pages/TransferComplete";
import OTPSetup from "./pages/OTPSetup";
import Unregister from "./pages/Unregister";
import PrivateRoute from "./components/PrivateRoute";

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
          {/* 공개 라우트 */}
          <Route path="/" element={<Main />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* 보호된 라우트 */}
          <Route
            path="/mypage"
            element={
              <PrivateRoute>
                <MyPage />
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
            path="/withdraw/complete"
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
            path="/transfer/complete"
            element={
              <PrivateRoute>
                <TransferComplete />
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
          <Route
            path="/unregister"
            element={
              <PrivateRoute>
                <Unregister />
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
