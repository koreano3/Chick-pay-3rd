import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Paper,
} from "@mui/material";
import axios from "axios";
import Layout from "../components/Layout";

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    birthdate: "",
    password1: "",
    password2: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password1 !== formData.password2) {
      alert("비밀번호가 일치하지 않습니다.");
      return;
    }

    try {
      const response = await axios.post(
        "http://127.0.0.1:8001/zapp/api/register/",
        {
          name: formData.name,
          email: formData.email,
          birthdate: formData.birthdate,
          password1: formData.password1,
          password2: formData.password2,
        }
      );

      if (response.status === 201) {
        alert("회원가입이 완료되었습니다.");
        navigate("/login");
      }
    } catch (error) {
      console.error("Registration failed:", error);
      alert("회원가입에 실패했습니다.");
    }
  };

  return (
    <Layout>
      <Container component="main" maxWidth="xs">
        <Box
          sx={{
            marginTop: 8,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Paper
            elevation={3}
            sx={{
              padding: 4,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              width: "100%",
            }}
          >
            <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
              Chick Pay 회원가입
            </Typography>
            <Box
              component="form"
              onSubmit={handleSubmit}
              sx={{ mt: 1, width: "100%" }}
            >
              <TextField
                margin="normal"
                required
                fullWidth
                id="name"
                label="이름"
                name="name"
                autoComplete="name"
                autoFocus
                value={formData.name}
                onChange={handleChange}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="email"
                label="이메일"
                type="email"
                id="email"
                autoComplete="email"
                value={formData.email}
                onChange={handleChange}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="birthdate"
                label="생년월일"
                id="birthdate"
                placeholder="예시 1994-03-05"
                value={formData.birthdate}
                onChange={handleChange}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password1"
                label="비밀번호"
                type="password"
                id="password1"
                autoComplete="new-password"
                value={formData.password1}
                onChange={handleChange}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password2"
                label="비밀번호 확인"
                type="password"
                id="password2"
                autoComplete="new-password"
                value={formData.password2}
                onChange={handleChange}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2, bgcolor: "primary.main" }}
              >
                회원가입
              </Button>
              <Button
                fullWidth
                variant="text"
                onClick={() => navigate("/login")}
                sx={{ mt: 1 }}
              >
                로그인으로 돌아가기
              </Button>
            </Box>
          </Paper>
        </Box>
      </Container>
    </Layout>
  );
};

export default Register;
