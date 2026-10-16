use crate::ast::{AstNode, BinaryOp, UnaryOp};
use crate::token::{Token, TokenType};

#[derive(Debug, Clone)]
pub struct ParserError {
    pub message: String,
    pub start: usize,
    pub end: usize,
}

pub struct Parser {
    tokens: Vec<Token>,
    cursor: usize,
    next_node_id: usize,
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        Self {
            tokens,
            cursor: 0,
            next_node_id: 1,
        }
    }

    fn gen_id(&mut self) -> usize {
        let id = self.next_node_id;
        self.next_node_id += 1;
        id
    }

    fn peek(&self) -> &Token {
        if self.cursor < self.tokens.len() {
            &self.tokens[self.cursor]
        } else {
            self.tokens.last().expect("Token stream cannot be empty")
        }
    }

    fn advance(&mut self) -> Token {
        let tok = self.peek().clone();
        if self.cursor < self.tokens.len() {
            self.cursor += 1;
        }
        tok
    }

    pub fn parse(&mut self) -> Result<AstNode, ParserError> {
        if self.peek().token_type == TokenType::Eof {
            return Err(ParserError {
                message: "Empty expression provided".to_string(),
                start: 0,
                end: 0,
            });
        }

        let mut root = self.parse_expression(0)?;

        let next = self.peek();
        if next.token_type != TokenType::Eof {
            return Err(ParserError {
                message: format!("Unexpected trailing token '{}' after valid expression", next.lexeme),
                start: next.start,
                end: next.end,
            });
        }

        root.compute_layout();
        Ok(root)
    }

    fn parse_expression(&mut self, min_precedence: u8) -> Result<AstNode, ParserError> {
        let mut left = self.parse_prefix()?;

        while let Some((op, left_prec, right_prec)) = self.peek_infix_precedence() {
            if left_prec < min_precedence {
                break;
            }

            // Consume operator token
            let _op_tok = self.advance();
            let right = self.parse_expression(right_prec)?;

            let span = (left.span.0, right.span.1);
            let id = self.gen_id();
            left = AstNode::new_binary(id, op, left, right, span);
        }

        Ok(left)
    }

    fn parse_prefix(&mut self) -> Result<AstNode, ParserError> {
        let token = self.advance();
        match token.token_type {
            TokenType::Number(val) => {
                let id = self.gen_id();
                Ok(AstNode::new_number(id, val, (token.start, token.end)))
            }
            TokenType::Minus => {
                let id = self.gen_id();
                let operand = self.parse_expression(40)?; // High precedence for unary minus
                let span = (token.start, operand.span.1);
                Ok(AstNode::new_unary(id, UnaryOp::Negate, operand, span))
            }
            TokenType::Plus => {
                let id = self.gen_id();
                let operand = self.parse_expression(40)?;
                let span = (token.start, operand.span.1);
                Ok(AstNode::new_unary(id, UnaryOp::Positive, operand, span))
            }
            TokenType::LParen => {
                let expr = self.parse_expression(0)?;
                let closing = self.advance();
                if closing.token_type != TokenType::RParen {
                    return Err(ParserError {
                        message: format!("Expected closing ')' to match '(' at position {}, found '{}'", token.start, closing.lexeme),
                        start: closing.start,
                        end: closing.end,
                    });
                }
                Ok(expr)
            }
            TokenType::RParen => Err(ParserError {
                message: "Unmatched closing parenthesis ')'".to_string(),
                start: token.start,
                end: token.end,
            }),
            TokenType::Eof => Err(ParserError {
                message: "Unexpected end of expression while parsing operand".to_string(),
                start: token.start,
                end: token.end,
            }),
            _ => Err(ParserError {
                message: format!("Expected number, unary operator, or '(', found '{}'", token.lexeme),
                start: token.start,
                end: token.end,
            }),
        }
    }

    fn peek_infix_precedence(&self) -> Option<(BinaryOp, u8, u8)> {
        match self.peek().token_type {
            TokenType::Plus => Some((BinaryOp::Add, 10, 11)),
            TokenType::Minus => Some((BinaryOp::Sub, 10, 11)),
            TokenType::Star => Some((BinaryOp::Mul, 20, 21)),
            TokenType::Slash => Some((BinaryOp::Div, 20, 21)),
            TokenType::Percent => Some((BinaryOp::Mod, 20, 21)),
            // Exponentiation is right-associative: left_prec < right_prec
            TokenType::Caret => Some((BinaryOp::Pow, 30, 29)),
            _ => None,
        }
    }
}
