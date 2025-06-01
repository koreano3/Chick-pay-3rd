import React from "react";
import { useNavigate } from "react-router-dom";
import { Container, Typography, Button, Box } from "@mui/material";

const Transfer = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        이체
      </Typography>
      <Box sx={{ mt: 2 }}>
        <Button variant="contained" onClick={() => navigate("/")}>
          메인으로 돌아가기
        </Button>
      </Box>
    </Container>
  );
};

export default Transfer;
