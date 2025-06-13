import React, { useState } from "react";
import {
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  InputAdornment,
  Alert,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "https://chick-pay.com";

  const Deposit: React.FC = () => {
  const [amount, setAmount] = useState("");
  const [memo, setMemo] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!amount || Number(amount) < 10) {
      setError("입금 금액은 10원 이상이어야 합니다.");
      return;
    }

    try {
      const access = localStorage.getItem("access_token");
      const response = await fetch(`${API_BASE_URL}/zapp/transaction/api/cash/deposit/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${access}`,
        },
        body: JSON.stringify({ amount, memo }),
      });

      const data = await response.json();

      if (response.ok) {
        alert("입금 성공! 현재 잔액: ₩" + data.balance);
        navigate("/deposit/complete", { state: { deposit: data } });
      } else {
        setError(data.error || "입금 실패");
      }
    } catch (err) {
      setError("네트워크 오류가 발생했습니다.");
    }
  };

  return (
    <Layout>
      <Container maxWidth="sm" sx={{ py: 6 }}>
        <Typography
          variant="h4"
          align="center"
          fontWeight={700}
          color="#7c4a03"
          mb={4}
        >
          입금하기
        </Typography>
        <Paper sx={{ p: 4, borderRadius: 4, border: "3px solid #ffe066" }}>
          <form onSubmit={handleSubmit}>
            <TextField
              label="입금 금액"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              fullWidth
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">₩</InputAdornment>
                ),
                inputProps: { min: 10, step: 1 },
              }}
              sx={{ mb: 3 }}
            />
            <TextField
              label="메모 (선택사항)"
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              fullWidth
              sx={{ mb: 4 }}
            />
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            <Button
              type="submit"
              variant="contained"
              fullWidth
              sx={{
                bgcolor: "#FFDE59",
                color: "#7c4a03",
                fontWeight: "bold",
                py: 2,
                borderRadius: 2,
                boxShadow: 2,
                "&:hover": { bgcolor: "#FFC93C" },
              }}
            >
              입금하기
            </Button>
          </form>
        </Paper>
      </Container>
    </Layout>
  );
};

export default Deposit;
