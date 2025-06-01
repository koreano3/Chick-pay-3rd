import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Box,
  Typography,
  Button,
  Grid,
  Paper,
  AppBar,
  Toolbar,
} from "@mui/material";
import axios from "axios";

const Main = () => {
  const navigate = useNavigate();
  const [balance, setBalance] = useState<number>(0);
  const [username, setUsername] = useState<string>("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }

    const fetchUserData = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8001/api/accounts/balance/",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        setBalance(response.data.balance);
        setUsername(response.data.username);
      } catch (error) {
        console.error("Failed to fetch user data:", error);
        if (axios.isAxiosError(error) && error.response?.status === 401) {
          navigate("/login");
        }
      }
    };

    fetchUserData();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/login");
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ bgcolor: "primary.main" }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Chick Pay
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            로그아웃
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            {username}님의 계좌
          </Typography>
          <Typography variant="h4" color="primary" gutterBottom>
            {balance.toLocaleString()}원
          </Typography>
        </Paper>

        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
          <Button
            fullWidth
            variant="contained"
            color="primary"
            onClick={() => navigate("/deposit")}
            sx={{ height: "100px", flex: 1 }}
          >
            입금
          </Button>
          <Button
            fullWidth
            variant="contained"
            color="primary"
            onClick={() => navigate("/withdraw")}
            sx={{ height: "100px", flex: 1 }}
          >
            출금
          </Button>
          <Button
            fullWidth
            variant="contained"
            color="primary"
            onClick={() => navigate("/transfer")}
            sx={{ height: "100px", flex: 1 }}
          >
            이체
          </Button>
        </Box>

        <Box sx={{ mt: 4 }}>
          <Button
            fullWidth
            variant="outlined"
            color="primary"
            onClick={() => navigate("/mypage")}
          >
            마이페이지
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default Main;
