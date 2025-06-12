import React, { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Avatar,
  TextField,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import Layout from "../components/Layout";

interface UserInfo {
  name: string;
  email: string;
  birthdate: string;
  balance: number;
}

const MyPage: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pwOpen, setPwOpen] = useState(false);
  const [pwForm, setPwForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [pwError, setPwError] = useState("");
  const [pwSuccess, setPwSuccess] = useState("");

  // 사용자 정보 불러오기
  useEffect(() => {
    const access = localStorage.getItem("access_token");
    if (!access) {
      navigate("/login");
      return;
    }

    // 1. 회원 정보(user-service)
    fetch("https://chick-pay.com/zapp/api/mypage/", {
      headers: { Authorization: `Bearer ${access}` },
    })
      .then(async (res) => {
        if (res.status === 401) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          navigate("/login");
          throw new Error("인증 실패");
        }
        if (!res.ok) throw new Error("서버 오류");
        return res.json();
      })
      .then((userData) => {
        // 2. 캐시 정보(transaction-service)
        fetch("https://chick-pay.com/zapp/transaction/api/cash/info/", {
          headers: { Authorization: `Bearer ${access}` },
        })
          .then((res) => res.json())
          .then((cashData) => {
            setUser({
              ...userData,
              balance: cashData.balance, // 잔액만 따로 합침
            });
            setLoading(false);
          })
          .catch((err) => {
            setError("캐시 정보 조회 실패: " + err.message);
            setLoading(false);
          });
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [navigate]);

  // 비밀번호 변경 핸들러
  const handlePwChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwError("");
    setPwSuccess("");
    const access = localStorage.getItem("access_token");
    if (!access) {
      navigate("/login");
      return;
    }
    try {
      const res = await fetch(
        "https://chick-pay.com/zapp/api/change-password/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${access}`,
          },
          body: JSON.stringify(pwForm),
        }
      );
      const result = await res.json();
      if (res.ok) {
        setPwSuccess(
          "비밀번호가 성공적으로 변경되었습니다. 새 비밀번호로 다시 로그인 해주세요."
        );
        setTimeout(() => {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          navigate("/login");
        }, 2000);
      } else {
        setPwError(result.error || "비밀번호 변경 실패");
      }
    } catch (err: any) {
      setPwError("요청 실패: " + err.message);
    }
  };

  if (loading)
    return (
      <Layout>
        <Container sx={{ mt: 8 }}>
          <Typography>로딩 중...</Typography>
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
  if (!user) return null;

  return (
    <Layout>
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Typography
          variant="h4"
          align="center"
          fontWeight={700}
          gutterBottom
          color="#7c4a03"
        >
          마이페이지
        </Typography>
        {/* 프로필 카드 */}
        <Paper
          elevation={3}
          sx={{ p: 4, mb: 3, border: "3px solid #ffe066", borderRadius: 5 }}
        >
          <Box
            sx={{
              display: "flex",
              flexDirection: { xs: "column", md: "row" },
              gap: 3,
              alignItems: "center",
            }}
          >
            <Box
              sx={{
                display: "flex",
                justifyContent: "center",
                width: { xs: "100%", md: "25%" },
              }}
            >
              <Avatar sx={{ width: 90, height: 90, bgcolor: "#ffe066" }}>
                <AccountCircleIcon sx={{ fontSize: 60, color: "#7c4a03" }} />
              </Avatar>
            </Box>
            <Box sx={{ width: { xs: "100%", md: "75%" } }}>
              <Typography variant="h6" color="#7c4a03">
                {user.name}
              </Typography>
              <Typography color="text.secondary">{user.email}</Typography>
              <Typography color="text.secondary">{user.birthdate}</Typography>
              <Box mt={2} display="flex" gap={2}>
                <Button
                  size="small"
                  onClick={() => setPwOpen(true)}
                  sx={{ color: "#7c4a03" }}
                >
                  비밀번호 변경
                </Button>
                <Button
                  size="small"
                  variant="contained"
                  color="error"
                  onClick={() => navigate("/unregister")}
                  sx={{ borderRadius: 3 }}
                >
                  회원탈퇴
                </Button>
              </Box>
            </Box>
          </Box>
        </Paper>
        {/* 비밀번호 변경 다이얼로그 */}
        <Dialog open={pwOpen} onClose={() => setPwOpen(false)}>
          <DialogTitle>비밀번호 변경</DialogTitle>
          <DialogContent>
            <Box component="form" onSubmit={handlePwChange} sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                label="현재 비밀번호"
                type="password"
                fullWidth
                required
                value={pwForm.current_password}
                onChange={(e) =>
                  setPwForm((f) => ({ ...f, current_password: e.target.value }))
                }
              />
              <TextField
                margin="normal"
                label="새 비밀번호"
                type="password"
                fullWidth
                required
                value={pwForm.new_password}
                onChange={(e) =>
                  setPwForm((f) => ({ ...f, new_password: e.target.value }))
                }
              />
              <TextField
                margin="normal"
                label="새 비밀번호 확인"
                type="password"
                fullWidth
                required
                value={pwForm.confirm_password}
                onChange={(e) =>
                  setPwForm((f) => ({ ...f, confirm_password: e.target.value }))
                }
              />
              {pwError && (
                <Alert severity="error" sx={{ mt: 1 }}>
                  {pwError}
                </Alert>
              )}
              {pwSuccess && (
                <Alert severity="success" sx={{ mt: 1 }}>
                  {pwSuccess}
                </Alert>
              )}
              <DialogActions>
                <Button onClick={() => setPwOpen(false)}>취소</Button>
                <Button type="submit" variant="contained" color="primary">
                  변경
                </Button>
              </DialogActions>
            </Box>
          </DialogContent>
        </Dialog>
        {/* 잔액 카드 */}
        <Paper
          elevation={3}
          sx={{ p: 4, mb: 3, border: "3px solid #ffe066", borderRadius: 5 }}
        >
          <Typography variant="h6" color="#7c4a03" gutterBottom>
            내 잔액 정보
          </Typography>
          <Box
            sx={{
              bgcolor: "linear-gradient(90deg, #ffe066 0%, #ffb347 100%)",
              borderRadius: 3,
              p: 3,
              display: "flex",
              alignItems: "center",
              gap: 2,
            }}
          >
            <span style={{ fontSize: 28 }}>🏦</span>
            <Box>
              <Typography fontWeight={700}>Chick-Pay 캐시</Typography>
              <Typography fontSize={20} fontWeight={700} color="#7c4a03">
                ₩ {Math.floor(user.balance).toLocaleString()}
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Layout>
  );
};

export default MyPage;
