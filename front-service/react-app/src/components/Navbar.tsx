import React, { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Box,
  Button,
  CircularProgress,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<{ name: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const access = localStorage.getItem("access_token");
    if (access) {
      fetch("https://chick-pay.com/zapp/api/user/me/", {
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

  return (
    <Box sx={{ bgcolor: "#FFDE59", py: 3, boxShadow: 2 }}>
      <Container maxWidth="lg">
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 2,
          }}
        >
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 2,
              flex: "1 1 auto",
              minWidth: 0,
            }}
          >
            <img
              src="/static/images/image.png"
              alt="Chick Pay"
              style={{ width: 50, height: "auto", cursor: "pointer" }}
              onClick={() => navigate("/")}
            />
            <Typography
              variant="h5"
              fontWeight={700}
              color="#B85C38"
              style={{ cursor: "pointer" }}
              onClick={() => navigate("/")}
            >
              Chick Pay
            </Typography>
            {user && (
              <Typography sx={{ ml: 2 }} color="grey.700">
                안녕하세요, <strong>{user.name}</strong>님!
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              display: { xs: "none", md: "flex" },
              gap: 3,
              mr: 4,
            }}
          >
            {user ? (
              <>
                <Button
                  sx={{
                    color: "#B85C38",
                    fontWeight: "bold",
                    "&:hover": { bgcolor: "rgba(184, 92, 56, 0.1)" },
                  }}
                  onClick={() => navigate("/transfer")}
                >
                  송금하기
                </Button>
                <Button
                  sx={{
                    color: "#B85C38",
                    fontWeight: "bold",
                    "&:hover": { bgcolor: "rgba(184, 92, 56, 0.1)" },
                  }}
                  onClick={() => navigate("/deposit")}
                >
                  입금하기
                </Button>
                <Button
                  sx={{
                    color: "#B85C38",
                    fontWeight: "bold",
                    "&:hover": { bgcolor: "rgba(184, 92, 56, 0.1)" },
                  }}
                  onClick={() => navigate("/withdraw")}
                >
                  출금하기
                </Button>
                <Button
                  sx={{
                    color: "#B85C38",
                    fontWeight: "bold",
                    "&:hover": { bgcolor: "rgba(184, 92, 56, 0.1)" },
                  }}
                  onClick={() => navigate("/mypage")}
                >
                  마이페이지
                </Button>
                <Button
                  sx={{
                    color: "#B85C38",
                    fontWeight: "bold",
                    "&:hover": { bgcolor: "rgba(184, 92, 56, 0.1)" },
                  }}
                  onClick={handleLogout}
                >
                  로그아웃
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="contained"
                  sx={{
                    bgcolor: "#B85C38",
                    color: "#fff",
                    fontWeight: "bold",
                    borderRadius: 2,
                    px: 3,
                    minWidth: { xs: "100%", sm: "auto" },
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
                    px: 3,
                    bgcolor: "#fff",
                    "&:hover": { bgcolor: "#FFF9E5" },
                    minWidth: { xs: "100%", sm: "auto" },
                  }}
                  onClick={() => navigate("/register")}
                >
                  회원가입
                </Button>
              </>
            )}
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Navbar;
