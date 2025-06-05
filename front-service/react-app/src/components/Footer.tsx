import React from "react";
import { Container, Typography, Box, Button } from "@mui/material";

const Footer: React.FC = () => (
  <Box sx={{ bgcolor: "#FFDE59", py: 5, mt: "auto" }}>
    <Container maxWidth="lg">
      <Box
        display="flex"
        flexDirection={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems="center"
        mb={4}
        gap={2}
      >
        <Box display="flex" alignItems="center" gap={2}>
          <img
            src="/static/images/image.png"
            alt="Chick Pay"
            style={{ width: 50, height: "auto" }}
          />
          <Typography variant="h5" fontWeight={700} color="#B85C38">
            Chick Pay
          </Typography>
        </Box>
        <Box display="flex" flexWrap="wrap" gap={3} justifyContent="center">
          <Button sx={{ color: "#B85C38" }}>서비스 소개</Button>
          <Button sx={{ color: "#B85C38" }}>이용약관</Button>
          <Button sx={{ color: "#B85C38" }}>개인정보처리방침</Button>
          <Button sx={{ color: "#B85C38" }}>고객센터</Button>
          <Button sx={{ color: "#B85C38" }}>채용정보</Button>
        </Box>
      </Box>
      <Typography textAlign="center" color="#B85C38">
        &copy; 2025 Chick Pay. 모든 권리 보유.
      </Typography>
    </Container>
  </Box>
);

export default Footer;
