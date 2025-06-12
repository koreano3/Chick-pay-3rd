import React, { useState } from "react";
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  TextField,
  FormControlLabel,
  Checkbox,
  Radio,
  RadioGroup,
  FormControl,
  FormLabel,
  Link,
  Alert,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { keyframes } from "@mui/system";
import Layout from "../components/Layout";

// 애니메이션 정의
const float = keyframes`
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
`;

const Unregister: React.FC = () => {
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirmChecked, setConfirmChecked] = useState(false);
  const [reason, setReason] = useState("");
  const [additionalComment, setAdditionalComment] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!confirmChecked) {
      setError("탈퇴 동의가 필요합니다.");
      return;
    }

    if (
      !window.confirm(
        "정말로 Chick Pay 회원에서 탈퇴하시겠습니까? 이 작업은 되돌릴 수 없습니다."
      )
    ) {
      return;
    }

    const access = localStorage.getItem("access_token");
    if (!access) {
      navigate("/login");
      return;
    }

    try {
      const response = await fetch(
        "https://chick-pay.com/zapp/api/unregister/",
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${access}`,
          },
          body: JSON.stringify({ password }),
        }
      );

      if (response.status === 204) {
        alert(
          "회원 탈퇴가 완료되었습니다. 그동안 Chick Pay를 이용해주셔서 감사합니다."
        );
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/");
        return;
      }

      const data = await response.json();
      const errorMsg = data.password
        ? data.password[0]
        : data.error || "알 수 없는 오류";
      setError(errorMsg);
    } catch (error) {
      console.error("네트워크 오류:", error);
      setError("서버 오류가 발생했습니다.");
    }
  };

  return (
    <Layout>
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Link
            component="button"
            variant="body2"
            onClick={() => navigate("/mypage")}
            sx={{ color: "#7c4a03", display: "flex", alignItems: "center" }}
          >
            ← 마이페이지로 돌아가기
          </Link>
        </Box>

        <Paper elevation={3} sx={{ p: { xs: 3, md: 5 }, borderRadius: 4 }}>
          <Box sx={{ textAlign: "center", mb: 4 }}>
            <Box sx={{ animation: `${float} 3s ease-in-out infinite`, mb: 2 }}>
              <Typography variant="h1" sx={{ fontSize: "4rem" }}>
                😢
              </Typography>
            </Box>
            <Typography
              variant="h4"
              sx={{ fontWeight: "bold", color: "#7c4a03", mb: 2 }}
            >
              회원탈퇴
            </Typography>
            <Typography
              color="text.secondary"
              sx={{ maxWidth: "xl", mx: "auto" }}
            >
              Chick Pay 서비스를 떠나신다니 정말 아쉽습니다. 탈퇴하기 전에 아래
              내용을 꼭 확인해주세요.
            </Typography>
          </Box>

          <Box sx={{ bgcolor: "#FEE2E2", p: 3, borderRadius: 3, mb: 4 }}>
            <Typography
              variant="h6"
              sx={{
                color: "#DC2626",
                mb: 2,
                display: "flex",
                alignItems: "center",
              }}
            >
              <span style={{ fontSize: "1.5rem", marginRight: "0.5rem" }}>
                ⚠️
              </span>
              탈퇴 전 주의사항
            </Typography>
            <Box component="ul" sx={{ pl: 2, color: "text.secondary" }}>
              <Box component="li" sx={{ mb: 1 }}>
                탈퇴 시 모든 계정 정보와 개인 데이터가{" "}
                <strong>영구적으로 삭제</strong>됩니다.
              </Box>
              <Box component="li" sx={{ mb: 1 }}>
                보유하신 포인트와 혜택이 모두 소멸되며, 복구가 불가능합니다.
              </Box>
              <Box component="li" sx={{ mb: 1 }}>
                진행 중인 거래나 이체가 있다면 모두 완료된 후에 탈퇴해주세요.
              </Box>
              <Box component="li">
                탈퇴 후 동일한 정보로 7일간 재가입이 제한됩니다.
              </Box>
            </Box>
          </Box>

          <Box sx={{ bgcolor: "#FFF9E5", p: 3, borderRadius: 3, mb: 4 }}>
            <Typography
              variant="h6"
              sx={{
                color: "#7c4a03",
                mb: 2,
                display: "flex",
                alignItems: "center",
              }}
            >
              <span style={{ fontSize: "1.5rem", marginRight: "0.5rem" }}>
                💬
              </span>
              탈퇴 이유를 알려주세요 (선택사항)
            </Typography>
            <FormControl component="fieldset">
              <RadioGroup
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              >
                <FormControlLabel
                  value="service"
                  control={<Radio />}
                  label="서비스 이용이 불편해요"
                />
                <FormControlLabel
                  value="no_need"
                  control={<Radio />}
                  label="더 이상 서비스가 필요하지 않아요"
                />
                <FormControlLabel
                  value="other_service"
                  control={<Radio />}
                  label="다른 서비스를 이용하려고 해요"
                />
                <FormControlLabel
                  value="privacy"
                  control={<Radio />}
                  label="개인정보 보호가 걱정돼요"
                />
                <FormControlLabel
                  value="etc"
                  control={<Radio />}
                  label="기타"
                />
              </RadioGroup>
            </FormControl>
            <TextField
              fullWidth
              multiline
              rows={3}
              placeholder="추가 의견이 있으시면 자유롭게 작성해주세요."
              value={additionalComment}
              onChange={(e) => setAdditionalComment(e.target.value)}
              sx={{ mt: 2 }}
            />
          </Box>

          <Box component="form" onSubmit={handleSubmit}>
            <Box sx={{ bgcolor: "grey.50", p: 3, borderRadius: 3, mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                본인 확인
              </Typography>
              <TextField
                fullWidth
                type="password"
                label="비밀번호 확인"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </Box>

            <FormControlLabel
              control={
                <Checkbox
                  checked={confirmChecked}
                  onChange={(e) => setConfirmChecked(e.target.checked)}
                  required
                />
              }
              label={
                <Typography sx={{ color: "error.main", fontWeight: "medium" }}>
                  위 주의사항을 모두 확인했으며, 회원탈퇴에 동의합니다.
                </Typography>
              }
              sx={{ mb: 3 }}
            />

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box
              sx={{
                display: "flex",
                gap: 2,
                justifyContent: "center",
                flexWrap: "wrap",
              }}
            >
              <Button
                variant="contained"
                color="inherit"
                onClick={() => navigate("/mypage")}
                sx={{ px: 4, py: 1.5, borderRadius: 2 }}
              >
                취소하기
              </Button>
              <Button
                type="submit"
                variant="contained"
                color="error"
                sx={{ px: 4, py: 1.5, borderRadius: 2 }}
              >
                회원탈퇴 😢
              </Button>
            </Box>
          </Box>

          <Typography
            variant="body2"
            color="text.secondary"
            align="center"
            sx={{ mt: 4 }}
          >
            문의사항이 있으신가요?{" "}
            <Link href="#" sx={{ color: "#7c4a03" }}>
              고객센터
            </Link>
            로 연락해주세요.
          </Typography>
        </Paper>

        <Paper elevation={3} sx={{ mt: 4, p: 3, borderRadius: 4 }}>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography
              variant="h3"
              sx={{
                mr: 2,
                animation: `${float} 3s ease-in-out infinite`,
              }}
            >
              🐥
            </Typography>
            <Box>
              <Typography
                variant="h6"
                sx={{ color: "#7c4a03", fontWeight: "bold" }}
              >
                아직 결정을 못 하셨나요?
              </Typography>
              <Typography variant="body2" color="text.secondary">
                잠시 서비스 이용을 중단하고 싶으시다면 계정 일시 정지를
                이용해보세요.
              </Typography>
              <Link
                href="#"
                sx={{
                  color: "#7c4a03",
                  display: "inline-block",
                  mt: 0.5,
                  fontSize: "0.875rem",
                  fontWeight: "medium",
                }}
              >
                계정 일시 정지 알아보기
              </Link>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Layout>
  );
};

export default Unregister;
