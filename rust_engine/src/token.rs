use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum TokenType {
    Number(f64),
    Plus,
    Minus,
    Star,
    Slash,
    Percent,
    Caret,
    LParen,
    RParen,
    Eof,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Token {
    pub token_type: TokenType,
    pub type_name: String,
    pub lexeme: String,
    pub start: usize,
    pub end: usize,
}

impl Token {
    pub fn new(token_type: TokenType, type_name: impl Into<String>, lexeme: impl Into<String>, start: usize, end: usize) -> Self {
        Self {
            token_type,
            type_name: type_name.into(),
            lexeme: lexeme.into(),
            start,
            end,
        }
    }
}
