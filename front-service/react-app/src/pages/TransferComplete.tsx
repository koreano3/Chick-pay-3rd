import React, { useEffect, useState } from "react";
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Divider,
  CircularProgress,
  Alert,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "https://chick-pay.com";

interface TransferData {
  sender_email: string;
  receiver_email: string;
  receiver_name: string;
  amount: number;
  memo?: string;
  created_at: string;
  transaction_id: string;
}

const TransferComplete: React.FC = () => {
  const [data, setData] = useState<TransferData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const access = localStorage.getItem("access_token");
    if (!access) {
      navigate("/login");
      return;
    }
    fetch(`${API_BASE_URL}/zapp/transaction/api/cash/transfer/complete/`, {
      headers: { Authorization: `Bearer ${access}` },
    })
      .then(async (res) => {
        if (res.status === 401) {
          navigate("/login");
          throw new Error("인증 실패");
        }
        if (!res.ok) throw new Error("서버 오류");
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [navigate]);

  if (loading)
    return (
      <Layout>
        <Container sx={{ mt: 8 }}>
          <CircularProgress />
        </Container>
      </Layout>
    );
  if (error)
    return (
      <Layout>
        <Container sx={{ mt: 8 }}>
          <Alert severity="error">{error}</Alert>
        </Container>
      </Layout>
    );
  if (!data) return null;

  return (
    <Layout>
      <Container
        maxWidth="sm"
        sx={{ py: 8, display: "flex", justifyContent: "center" }}
      >
        <Box width="100%" maxWidth={480}>
          <Paper
            elevation={3}
            sx={{
              p: 4,
              borderRadius: 5,
              border: "3px solid #ffe066",
              textAlign: "center",
            }}
          >
            <Box mb={3}>
              <img
                src="/static/images/image.png"
                alt="Chick Pay"
                style={{ width: 60, height: 60, marginBottom: 16 }}
              />
            </Box>
            <Typography
              variant="h5"
              fontWeight={700}
              color="#7c4a03"
              gutterBottom
            >
              송금이 완료되었습니다!
            </Typography>
            <Typography color="text.secondary" mb={4}>
              송금 내역을 확인하세요.
            </Typography>

            <Box
              sx={{
                bgcolor: "#fffde7",
                borderRadius: 3,
                p: 3,
                mb: 4,
                textAlign: "left",
              }}
            >
              <Box display="flex" justifyContent="space-between" mb={1}>
                <span className="text-gray-600">보낸 계좌</span>
                <span>{data.sender_email}</span>
              </Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <span className="text-gray-600">받는 계좌</span>
                <span>{data.receiver_email}</span>
              </Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <span className="text-gray-600">받는 분</span>
                <span>{data.receiver_name}</span>
              </Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <span className="text-gray-600">송금 금액</span>
                <span
                  style={{ fontWeight: 700, fontSize: 20, color: "#7c4a03" }}
                >
                  ₩ {data.amount.toLocaleString()}
                </span>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <span className="text-gray-600">메모</span>
                <span>{data.memo || "-"}</span>
              </Box>
            </Box>

            <Divider sx={{ mb: 2 }} />
            <Box
              display="flex"
              justifyContent="space-between"
              mb={1}
              fontSize={14}
              color="#888"
            >
              <span>거래 번호</span>
              <span>{data.transaction_id}</span>
            </Box>
            <Box
              display="flex"
              justifyContent="space-between"
              mb={3}
              fontSize={14}
              color="#888"
            >
              <span>거래 일시</span>
              <span>{data.created_at}</span>
            </Box>

            <Box display="flex" gap={2} mt={2}>
              <Button
                fullWidth
                variant="outlined"
                sx={{ bgcolor: "#f5f5f5", color: "#7c4a03", fontWeight: 700 }}
                onClick={() => navigate("/transfer")}
              >
                다시 송금하기
              </Button>
              <Button
                fullWidth
                variant="contained"
                sx={{
                  bgcolor: "#ffe066",
                  color: "#7c4a03",
                  fontWeight: 700,
                  "&:hover": { bgcolor: "#ffc93c" },
                }}
                onClick={() => navigate("/")}
              >
                메인으로
              </Button>
            </Box>
          </Paper>
        </Box>
      </Container>
    </Layout>
  );
};

export default TransferComplete;
