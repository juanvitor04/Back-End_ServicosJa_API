import re
from django.core.exceptions import ValidationError

def clean_digits(value):
    if not value:
        return ""
    return re.sub(r'\D', '', str(value))

def validar_cpf(cpf):
    cpf = clean_digits(cpf)
    
    if len(cpf) != 11:
        raise ValidationError("O CPF deve conter exatamente 11 dígitos.")

    return cpf

def validar_telefone(telefone):
    telefone = clean_digits(telefone)
    
    if len(telefone) != 11:
        raise ValidationError("O telefone deve conter exatamente 11 dígitos (DDD + 9 números).")
    
    return telefone

def validar_cep(cep):
    cep = clean_digits(cep)
    
    if len(cep) != 8:
        raise ValidationError("O CEP deve conter exatamente 8 dígitos.")
    
    return cep
