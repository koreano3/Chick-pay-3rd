import React from "react";
import Navbar from "./Navbar";
import Footer from "./Footer";
import { Box } from "@mui/material";

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Box
    sx={{
      bgcolor: "#FFF9E5",
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
    }}
  >
    <Navbar />
    <Box sx={{ flex: 1 }}>{children}</Box>
    <Footer />
  </Box>
);

export default Layout;
