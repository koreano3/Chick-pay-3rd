# resource "kubernetes_config_map" "aws_auth" {
#   provider = kubernetes.eks

#   metadata {
#     name      = "aws-auth"
#     namespace = "kube-system"
#   }

#   data = {
#     mapRoles = yamlencode([
#       {
#         rolearn  = "arn:aws:iam::297195401389:role/EKSNodeRole"
#         username = "system:node:{{EC2PrivateDNSName}}"
#         groups   = ["system:bootstrappers", "system:nodes"]
#       }
#     ])

#     mapUsers = yamlencode([
#       {
#         userarn  = "arn:aws:iam::297195401389:user/jaesung"
#         username = "jaesung"
#         groups   = ["system:masters"]
#       },
#       {
#         userarn  = "arn:aws:iam::297195401389:user/eunsan"
#         username = "eunsan"
#         groups   = ["system:masters"]
#       },
#       {
#         userarn  = "arn:aws:iam::297195401389:user/sujin"
#         username = "sujin"
#         groups   = ["system:masters"]
#       },
#       {
#         userarn  = "arn:aws:iam::297195401389:user/eomsigi"
#         username = "eomsigi"
#         groups   = ["system:masters"]
#       }
#     ])
#   }

#   depends_on = [null_resource.wait_for_eks]
# }
