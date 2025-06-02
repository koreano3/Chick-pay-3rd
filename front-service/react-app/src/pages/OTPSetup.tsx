import React from "react";
import { useNavigate } from "react-router-dom";
import { Container, Typography, Button, Box } from "@mui/material";
import Layout from "../components/Layout";

const OTPSetup = () => {
  const navigate = useNavigate();

  return (
    <Layout>
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          OTP 설정
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Button variant="contained" onClick={() => navigate("/")}>
            메인으로 돌아가기
          </Button>
        </Box>
      </Container>
    </Layout>
  );
};

export default OTPSetup;
