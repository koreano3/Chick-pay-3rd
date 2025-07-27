import React, { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  CircularProgress,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";

const features = [
  {
    icon: "💸",
    title: "간편 송금",
    desc: "친구나 가족에게 쉽고 빠르게 돈을 보낼 수 있습니다. 수수료 없이 즉시 이체됩니다.",
  },
  {
    icon: "🔒",
    title: "안전한 결제",
    desc: "최신 보안 기술로 안전하게 결제하세요. 모든 거래는 암호화되어 보호됩니다.",
  },
  {
    icon: "📊",
    title: "지출 분석",
    desc: "소비 패턴을 분석하여 현명한 금융 결정을 도와드립니다. 맞춤형 리포트를 제공합니다.",
  },
];

const reviews = [
  {
    stars: "⭐⭐⭐⭐⭐",
    text: "Chick Pay는 정말 사용하기 쉽고 귀여워요! 송금할 때마다 기분이 좋아집니다. 다른 금융 앱과는 차원이 다릅니다.",
    name: "배재성, 27세",
  },
  {
    stars: "⭐⭐⭐⭐⭐",
    text: "지출 분석 기능이 정말 유용해요. 덕분에 불필요한 지출을 줄이고 저축을 늘릴 수 있었습니다. 강력 추천합니다!",
    name: "김수진, 17세",
  },
  {
    stars: "⭐⭐⭐⭐⭐",
    text: "보안이 철저하면서도 사용이 간편해요. 특히 자동 저축 기능 덕분에 목표 금액을 쉽게 모을 수 있었습니다.",
    name: "엄현진, 20세",
  },
];

const Main: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<{ name: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const access = localStorage.getItem("access_token");
    if (access) {
      fetch(`https://chick-pay.com/zapp/api/user/me/`, {
        headers: { Authorization: `Bearer ${access}` },
      })
        .then((res) => {
          if (res.status === 401) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            setUser(null);
            setLoading(false);
            return;
          }
          if (!res.ok) throw new Error("서버 오류");
          return res.json();
        })
        .then((data) => {
          if (data) setUser({ name: data.name });
          setLoading(false);
        })
        .catch(() => {
          setUser(null);
          setLoading(false);
        });
    } else {
      setUser(null);
      setLoading(false);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/");
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Layout>
      {/* Hero Section */}
      <Box
        sx={{
          background: "linear-gradient(to bottom, #FFDE59, #FFF9E5)",
          py: { xs: 8, md: 12 },
        }}
      >
        <Container maxWidth="lg">
          <Box
            sx={{
              display: "flex",
              flexWrap: "wrap",
              gap: 6,
              alignItems: "center",
            }}
          >
            <Box sx={{ flex: "1 1 300px", minWidth: 0 }}>
              <Typography
                variant="h3"
                fontWeight={700}
                color="#B85C38"
                mb={3}
                sx={{ lineHeight: 1.2 }}
              >
                가장 귀여운
                <br />
                금융 서비스
              </Typography>
              <Typography variant="h6" mb={4} color="text.secondary">
                Chick Pay와 함께 간편하고 안전하게 송금, 입금, 출금을
                경험해보세요. 귀여운 디자인과 함께 금융 생활이 더욱
                즐거워집니다.
              </Typography>
              {!user && (
                <Box display="flex" gap={2} flexWrap="wrap">
                  <Button
                    variant="contained"
                    sx={{
                      bgcolor: "#B85C38",
                      color: "#fff",
                      fontWeight: "bold",
                      borderRadius: 2,
                      px: 4,
                    }}
                    onClick={() => navigate("/login")}
                  >
                    로그인하기
                  </Button>
                  <Button
                    variant="outlined"
                    sx={{
                      color: "#B85C38",
                      borderColor: "#B85C38",
                      fontWeight: "bold",
                      borderRadius: 2,
                      px: 4,
                      bgcolor: "#fff",
                      "&:hover": { bgcolor: "#FFF9E5" },
                    }}
                    onClick={() => navigate("/register")}
                  >
                    회원가입
                  </Button>
                </Box>
              )}
            </Box>
            <Box sx={{ flex: "1 1 300px", minWidth: 0, textAlign: "center" }}>
              <Box
                sx={{
                  width: { xs: 220, md: 320 },
                  height: { xs: 220, md: 320 },
                  mx: "auto",
                  bgcolor: "#fff",
                  borderRadius: "50%",
                  boxShadow: 3,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  position: "relative",
                }}
              >
                <img
                  src="/static/images/image.png"
                  alt="Chick Pay"
                  style={{
                    width: 120,
                    height: 120,
                    animation: "float 3s ease-in-out infinite",
                  }}
                />
                <Box
                  sx={{
                    position: "absolute",
                    top: -20,
                    right: -20,
                    bgcolor: "#FFC93C",
                    color: "#B85C38",
                    fontWeight: "bold",
                    px: 2,
                    py: 1,
                    borderRadius: 3,
                    boxShadow: 2,
                    transform: "rotate(12deg)",
                  }}
                >
                  신규 가입 혜택!
                </Box>
                <Box
                  sx={{
                    position: "absolute",
                    bottom: -12,
                    left: -12,
                    bgcolor: "#fff",
                    color: "#B85C38",
                    fontWeight: "bold",
                    px: 2,
                    py: 1,
                    borderRadius: 3,
                    boxShadow: 2,
                    transform: "rotate(-6deg)",
                  }}
                >
                  수수료 무료!
                </Box>
              </Box>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* 기능 섹션 */}
      <Box sx={{ py: 10 }}>
        <Container maxWidth="lg">
          <Typography
            variant="h4"
            fontWeight={700}
            color="#B85C38"
            textAlign="center"
            mb={6}
          >
            Chick Pay의 특별한 기능
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
            {features.map((f, i) => (
              <Box key={i} sx={{ flex: "1 1 300px", minWidth: 0 }}>
                <Paper
                  sx={{
                    p: 4,
                    borderRadius: 5,
                    border: "2px solid #FFDE59",
                    boxShadow: 3,
                    textAlign: "center",
                    transition: "0.2s",
                    "&:hover": {
                      borderColor: "#FFC93C",
                      transform: "translateY(-8px)",
                    },
                  }}
                >
                  <Typography fontSize={48} mb={2}>
                    {f.icon}
                  </Typography>
                  <Typography
                    variant="h6"
                    fontWeight={700}
                    color="#B85C38"
                    mb={1}
                  >
                    {f.title}
                  </Typography>
                  <Typography color="text.secondary">{f.desc}</Typography>
                </Paper>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      {/* 후기 섹션 */}
      <Box sx={{ py: 10, bgcolor: "#FFF9E5" }}>
        <Container maxWidth="lg">
          <Typography
            variant="h4"
            fontWeight={700}
            color="#B85C38"
            textAlign="center"
            mb={6}
          >
            고객 후기
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
            {reviews.map((r, i) => (
              <Box key={i} sx={{ flex: "1 1 300px", minWidth: 0 }}>
                <Paper sx={{ p: 4, borderRadius: 5, textAlign: "center" }}>
                  <Typography fontSize={32} mb={2}>
                    {r.stars}
                  </Typography>
                  <Typography color="text.secondary" mb={3}>
                    "{r.text}"
                  </Typography>
                  <Typography fontWeight={700}>{r.name}</Typography>
                </Paper>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>
    </Layout>
  );
};

export default Main;
