import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Paper,
  InputAdornment,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8002";

const Transfer: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    receiver_email: "",
    amount: "",
    memo: "",
  });
  const [userInfo, setUserInfo] = useState({
    name: "",
    email: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // 사용자 정보 가져오기
    const fetchUserInfo = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/zapp/api/mypage/`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setUserInfo({
            name: data.name,
            email: data.email,
          });
        }
      } catch (error) {
        console.error("사용자 정보 조회 실패:", error);
      }
    };

    fetchUserInfo();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/zapp/api/cash/transfer/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        alert(data.message || "송금 성공!");
        navigate("/transfer/complete");
      } else {
        const firstErrorKey = Object.keys(data)[0];
        const firstErrorMessage = data[firstErrorKey][0];
        setError(firstErrorMessage || "알 수 없는 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error("송금 실패:", error);
      setError("서버 연결에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <Layout>
      <Box sx={{ bgcolor: "#FFF9E5", minHeight: "100vh", py: 4 }}>
        <Container maxWidth="sm">
          <Typography
            variant="h4"
            component="h1"
            sx={{
              textAlign: "center",
              color: "#B85C38",
              fontWeight: 700,
              mb: 4,
            }}
          >
            송금하기
          </Typography>

          <Paper
            elevation={3}
            sx={{
              p: 4,
              borderRadius: 4,
              border: "3px solid #FFDE59",
              bgcolor: "#fff",
            }}
          >
            <form onSubmit={handleSubmit}>
              <Box sx={{ mb: 3 }}>
                <Typography
                  variant="subtitle1"
                  sx={{ color: "text.secondary", mb: 1 }}
                >
                  보내는 사람
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  {userInfo.name}
                </Typography>
                <Typography variant="body2" sx={{ color: "text.secondary" }}>
                  {userInfo.email}
                </Typography>
              </Box>

              <TextField
                fullWidth
                label="받는 사람 이메일"
                name="receiver_email"
                value={formData.receiver_email}
                onChange={handleChange}
                required
                sx={{ mb: 3 }}
                placeholder="받는 분 이메일을 입력하세요"
              />

              <TextField
                fullWidth
                label="송금 금액"
                name="amount"
                type="number"
                value={formData.amount}
                onChange={handleChange}
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">₩</InputAdornment>
                  ),
                }}
                sx={{ mb: 3 }}
                placeholder="0"
              />

              <TextField
                fullWidth
                label="메모 (선택사항)"
                name="memo"
                value={formData.memo}
                onChange={handleChange}
                sx={{ mb: 4 }}
                placeholder="메모를 입력하세요"
              />

              {error && (
                <Typography color="error" sx={{ mb: 2 }}>
                  {error}
                </Typography>
              )}

              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{
                  bgcolor: "#FFDE59",
                  color: "#B85C38",
                  py: 1.5,
                  fontSize: "1.1rem",
                  fontWeight: 700,
                  "&:hover": {
                    bgcolor: "#FFC93C",
                  },
                }}
              >
                {loading ? "송금 중..." : "송금하기"}
              </Button>
            </form>
          </Paper>
        </Container>
      </Box>
    </Layout>
  );
};

export default Transfer;
