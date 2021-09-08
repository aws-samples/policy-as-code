package security_group

default deny_non_secured_ports = true

deny_non_secured_ports = false  {
    some resource,j
    input.Resources[resource].Type == "AWS::EC2::SecurityGroup"
    input.Resources[resource].Properties.SecurityGroupIngress
    input.Resources[resource].Properties.SecurityGroupIngress[j].FromPort == 443
}