# VPC 생성: 기본 네트워크의 범위를 정의
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr   # 예: "10.0.0.0/16"
  enable_dns_support   = true           # 인스턴스가 DNS로 외부와 통신 가능하게 함
  enable_dns_hostnames = true           # 퍼블릭 IP에 대해 DNS 호스트네임 부여 가능
  tags = {
    Name = "vpc-for-cicdEKS"
  }
}

# 인터넷 게이트웨이 생성: VPC 외부 인터넷과 통신하기 위한 장치
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id       # 위에서 만든 VPC와 연결
  tags = {
    Name = "main-igw"
  }
}

# 퍼블릭 서브넷 생성: 인터넷과 직접 통신 가능한 서브넷
resource "aws_subnet" "public" {
  count                   = length(var.public_subnets)    # 서브넷 개수만큼 반복 생성
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnets[count.index]   # 예: ["10.0.1.0/24", ...]
  availability_zone       = element(var.azs, count.index)     # 예: ["ap-northeast-2a", ...]
  map_public_ip_on_launch = true         # 인스턴스가 자동으로 퍼블릭 IP 할당받음
  tags = {
    Name = "public-${count.index}"
  }
}

# 프라이빗 서브넷 생성: 외부 인터넷과 직접 통신은 불가능한 내부 서브넷
resource "aws_subnet" "private" {
  count             = length(var.private_subnets)          # 서브넷 개수만큼 반복 생성
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnets[count.index]     # 예: ["10.0.101.0/24", ...]
  availability_zone = element(var.azs, count.index)
  tags = {
    Name = "private-${count.index}"
  }
}

# NAT Gateway를 위한 탄력적 IP (EIP) 할당
resource "aws_eip" "nat" {
  vpc = true   # VPC 전용 EIP 할당 (Classic AWS 아닌 VPC 환경용)
}

# NAT Gateway 생성: 프라이빗 서브넷이 인터넷으로 나갈 수 있도록 지원
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id                   # 위에서 만든 EIP와 연결
  subnet_id     = aws_subnet.public[0].id          # 퍼블릭 서브넷에 위치시켜야 함
  tags = {
    Name = "nat-gateway"
  }
}

# 퍼블릭 라우트 테이블 생성: 인터넷 게이트웨이와 연결된 라우팅
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"                       # 모든 외부 트래픽
    gateway_id = aws_internet_gateway.igw.id      # IGW를 통해 나감
  }
  tags = {
    Name = "public-rt"
  }
}

# 퍼블릭 서브넷에 퍼블릭 라우트 테이블 연결
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# 프라이빗 라우트 테이블 생성: NAT Gateway 경유하여 외부와 통신 가능하게 함
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }
  tags = {
    Name = "private-rt"
  }
}

# 프라이빗 서브넷에 프라이빗 라우트 테이블 연결
resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}
