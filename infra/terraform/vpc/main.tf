# VPC 생성: 전체 네트워크 범위를 정의하고 AWS 내 자원들을 논리적으로 묶어줌
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true  # 인스턴스가 DNS로 외부와 통신할 수 있게 함
  enable_dns_hostnames = true  # 퍼블릭 IP에 대해 호스트네임 부여 가능

  tags = {
    Name = "vpc-for-eks-chickpay-service"
  }
}

# 인터넷 게이트웨이 생성: 퍼블릭 서브넷이 인터넷과 통신할 수 있게 해줌
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "eks-chickpay-igw"
  }
}

# 퍼블릭 서브넷: 외부에서 직접 접근 가능한 서브넷으로 ALB와 NAT Gateway 등을 배치함
resource "aws_subnet" "public" {
  count                   = length(var.public_subnets)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnets[count.index]
  availability_zone       = element(var.azs, count.index)
  map_public_ip_on_launch = true  # 인스턴스가 자동으로 퍼블릭 IP를 할당받음

  tags = {
    Name = "chickpay-public-${count.index}"
    "kubernetes.io/role/elb"                    = "1"  # ALB가 이 서브넷을 사용할 수 있게 함
    "kubernetes.io/cluster/eks-chickpay-service" = "shared"  # EKS 클러스터에서 이 서브넷을 공유함
  }
}

# 프라이빗 서브넷: 외부 접근이 불가능한 내부 서브넷. EKS 노드 등이 배치됨
resource "aws_subnet" "private" {
  count             = length(var.private_subnets)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnets[count.index]
  availability_zone = element(var.azs, count.index)

  tags = {
    Name = "chickpay-private-${count.index}"
    "kubernetes.io/cluster/eks-chickpay-service" = "shared"  # EKS 클러스터에서 이 서브넷을 공유함
  }
}

# NAT Gateway를 위한 퍼블릭 IP 할당: 프라이빗 서브넷이 외부로 나갈 때 사용
resource "aws_eip" "nat" {
    domain = "vpc"
}

# NAT Gateway: 프라이빗 서브넷에서 외부 인터넷으로 나갈 수 있게 함
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id  # 퍼블릭 서브넷에 위치해야 함

  tags = {
    Name = "chickpay-nat"
  }
}

# 퍼블릭 라우트 테이블: 퍼블릭 서브넷이 IGW를 통해 외부와 통신할 수 있도록 라우팅
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "chickpay-public-rt"
  }
}

# 퍼블릭 서브넷에 퍼블릭 라우트 테이블 연결
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# 프라이빗 라우트 테이블: NAT Gateway를 통해 외부로 나가는 라우팅 설정
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name = "chickpay-private-rt"
  }
}

# 프라이빗 서브넷에 프라이빗 라우트 테이블 연결
resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}