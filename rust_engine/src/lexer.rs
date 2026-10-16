use crate::token::{Token, TokenType};

#[derive(Debug, Clone)]
pub struct LexerError {
    pub message: String,
    pub position: usize,
}

pub struct Lexer<'a> {
    chars: Vec<(usize, char)>,
    cursor: usize,
    length: usize,
    _source: &'a str,
}

impl<'a> Lexer<'a> {
    pub fn new(source: &'a str) -> Self {
        let chars: Vec<(usize, char)> = source.char_indices().collect();
        let length = chars.len();
        Self {
            chars,
            cursor: 0,
            length,
            _source: source,
        }
    }

    fn peek(&self) -> Option<char> {
        if self.cursor < self.length {
            Some(self.chars[self.cursor].1)
        } else {
            None
        }
    }

    fn peek_next(&self) -> Option<char> {
        if self.cursor + 1 < self.length {
            Some(self.chars[self.cursor + 1].1)
        } else {
            None
        }
    }

    fn advance(&mut self) -> Option<(usize, char)> {
        if self.cursor < self.length {
            let item = self.chars[self.cursor];
            self.cursor += 1;
            Some(item)
        } else {
            None
        }
    }

    fn current_pos(&self) -> usize {
        if self.cursor < self.length {
            self.chars[self.cursor].0
        } else if let Some(last) = self.chars.last() {
            last.0 + last.1.len_utf8()
        } else {
            0
        }
    }

    pub fn tokenize(&mut self) -> Result<Vec<Token>, LexerError> {
        let mut tokens = Vec::new();

        while let Some(ch) = self.peek() {
            if ch.is_whitespace() {
                self.advance();
                continue;
            }

            let start_pos = self.current_pos();

            match ch {
                '+' => {
                    self.advance();
                    tokens.push(Token::new(TokenType::Plus, "PLUS", "+", start_pos, start_pos + 1));
                }
                '-' => {
                    self.advance();
                    tokens.push(Token::new(TokenType::Minus, "MINUS", "-", start_pos, start_pos + 1));
                }
                '*' => {
                    self.advance();
                    tokens.push(Token::new(TokenType::Star, "STAR", "*", start_pos, start_pos + 1));
                }
                '/' => {
                    self.advance();
                    tokens.push(Token::new(TokenType::Slash, "SLASH", "/", start_pos, start_pos + 1));
                }
                '%' => {
                    self.advance();
                    tokens.push(Token::new(TokenType::Percent, "PERCENT", "%", start_pos, start_pos + 1));
                }
                '^' => {
                    self.advance();
                    tokens.push(Token::new(TokenType::Caret, "CARET", "^", start_pos, start_pos + 1));
                }
                '(' => {
                    self.advance();
                    tokens.push(Token::new(TokenType::LParen, "LPAREN", "(", start_pos, start_pos + 1));
                }
                ')' => {
                    self.advance();
                    tokens.push(Token::new(TokenType::RParen, "RPAREN", ")", start_pos, start_pos + 1));
                }
                '0'..='9' | '.' => {
                    let num_token = self.lex_number(start_pos)?;
                    tokens.push(num_token);
                }
                other => {
                    return Err(LexerError {
                        message: format!("Unexpected character: '{}'", other),
                        position: start_pos,
                    });
                }
            }
        }

        let eof_pos = self.current_pos();
        tokens.push(Token::new(TokenType::Eof, "EOF", "", eof_pos, eof_pos));
        Ok(tokens)
    }

    fn lex_number(&mut self, start_pos: usize) -> Result<Token, LexerError> {
        let mut lexeme = String::new();
        let mut has_decimal = false;
        let mut has_exponent = false;

        // Check if starts with '.'
        if self.peek() == Some('.') {
            if let Some(next) = self.peek_next() {
                if next.is_ascii_digit() {
                    lexeme.push('.');
                    has_decimal = true;
                    self.advance();
                } else {
                    return Err(LexerError {
                        message: "Invalid stray '.' without digits".to_string(),
                        position: start_pos,
                    });
                }
            } else {
                return Err(LexerError {
                    message: "Invalid stray '.' without digits".to_string(),
                    position: start_pos,
                });
            }
        }

        while let Some(ch) = self.peek() {
            if ch.is_ascii_digit() {
                lexeme.push(ch);
                self.advance();
            } else if ch == '.' && !has_decimal && !has_exponent {
                has_decimal = true;
                lexeme.push(ch);
                self.advance();
            } else if (ch == 'e' || ch == 'E') && !has_exponent {
                has_exponent = true;
                lexeme.push(ch);
                self.advance();

                // Check optional sign after exponent
                if let Some(sign) = self.peek() {
                    if sign == '+' || sign == '-' {
                        lexeme.push(sign);
                        self.advance();
                    }
                }

                // Exponent must have at least one digit
                if let Some(exp_ch) = self.peek() {
                    if exp_ch.is_ascii_digit() {
                        lexeme.push(exp_ch);
                        self.advance();
                    } else {
                        return Err(LexerError {
                            message: "Expected exponent digits after 'e'".to_string(),
                            position: self.current_pos(),
                        });
                    }
                } else {
                    return Err(LexerError {
                        message: "Expected exponent digits after 'e'".to_string(),
                        position: self.current_pos(),
                    });
                }
            } else {
                break;
            }
        }

        let end_pos = self.current_pos();
        match lexeme.parse::<f64>() {
            Ok(val) => Ok(Token::new(TokenType::Number(val), "NUMBER", lexeme, start_pos, end_pos)),
            Err(e) => Err(LexerError {
                message: format!("Failed to parse number '{}': {}", lexeme, e),
                position: start_pos,
            }),
        }
    }
}
