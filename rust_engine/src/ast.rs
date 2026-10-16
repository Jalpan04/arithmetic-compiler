use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum BinaryOp {
    Add,
    Sub,
    Mul,
    Div,
    Mod,
    Pow,
}

impl BinaryOp {
    pub fn as_str(&self) -> &'static str {
        match self {
            BinaryOp::Add => "+",
            BinaryOp::Sub => "-",
            BinaryOp::Mul => "*",
            BinaryOp::Div => "/",
            BinaryOp::Mod => "%",
            BinaryOp::Pow => "^",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum UnaryOp {
    Negate,
    Positive,
}

impl UnaryOp {
    pub fn as_str(&self) -> &'static str {
        match self {
            UnaryOp::Negate => "-",
            UnaryOp::Positive => "+",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub enum AstKind {
    #[default]
    Empty,
    Number(f64),
    Unary {
        op: UnaryOp,
        expr: Box<AstNode>,
    },
    Binary {
        op: BinaryOp,
        left: Box<AstNode>,
        right: Box<AstNode>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AstNode {
    pub id: usize,
    pub label: String,
    pub node_type: String,
    pub value: Option<f64>,
    pub op: Option<String>,
    pub span: (usize, usize),
    pub depth: usize,
    pub x: f32,
    pub y: f32,
    pub children: Vec<AstNode>,
    #[serde(skip)]
    pub kind: AstKind,
}

impl AstNode {
    pub fn new_number(id: usize, val: f64, span: (usize, usize)) -> Self {
        Self {
            id,
            label: format!("{}", val),
            node_type: "Number".to_string(),
            value: Some(val),
            op: None,
            span,
            depth: 0,
            x: 0.0,
            y: 0.0,
            children: Vec::new(),
            kind: AstKind::Number(val),
        }
    }

    pub fn new_unary(id: usize, op: UnaryOp, expr: AstNode, span: (usize, usize)) -> Self {
        let label = format!("Unary ({})", op.as_str());
        let op_str = op.as_str().to_string();
        let child = expr.clone();
        Self {
            id,
            label,
            node_type: "UnaryOp".to_string(),
            value: None,
            op: Some(op_str),
            span,
            depth: 0,
            x: 0.0,
            y: 0.0,
            children: vec![child],
            kind: AstKind::Unary {
                op,
                expr: Box::new(expr),
            },
        }
    }

    pub fn new_binary(id: usize, op: BinaryOp, left: AstNode, right: AstNode, span: (usize, usize)) -> Self {
        let label = format!("Op ({})", op.as_str());
        let op_str = op.as_str().to_string();
        let l_child = left.clone();
        let r_child = right.clone();
        Self {
            id,
            label,
            node_type: "BinaryOp".to_string(),
            value: None,
            op: Some(op_str),
            span,
            depth: 0,
            x: 0.0,
            y: 0.0,
            children: vec![l_child, r_child],
            kind: AstKind::Binary {
                op,
                left: Box::new(left),
                right: Box::new(right),
            },
        }
    }

    /// Recursively computes subtree depths and layouts nodes using a neat hierarchical distribution
    pub fn compute_layout(&mut self) {
        self.assign_depths(0);
        let mut leaf_index = 0.0f32;
        self.assign_horizontal_positions(&mut leaf_index);
        self.normalize_center();
    }

    fn assign_depths(&mut self, current_depth: usize) {
        self.depth = current_depth;
        self.y = current_depth as f32 * 100.0;
        for child in &mut self.children {
            child.assign_depths(current_depth + 1);
        }
    }

    fn assign_horizontal_positions(&mut self, leaf_index: &mut f32) {
        if self.children.is_empty() {
            self.x = *leaf_index * 120.0;
            *leaf_index += 1.0;
        } else {
            for child in &mut self.children {
                child.assign_horizontal_positions(leaf_index);
            }
            let first_x = self.children.first().map(|c| c.x).unwrap_or(0.0);
            let last_x = self.children.last().map(|c| c.x).unwrap_or(0.0);
            self.x = (first_x + last_x) / 2.0;
        }
    }

    fn normalize_center(&mut self) {
        let center_offset = self.x;
        self.apply_offset(-center_offset);
    }

    fn apply_offset(&mut self, offset: f32) {
        self.x += offset;
        for child in &mut self.children {
            child.apply_offset(offset);
        }
    }

    pub fn tree_depth(&self) -> usize {
        if self.children.is_empty() {
            1
        } else {
            1 + self.children.iter().map(|c| c.tree_depth()).max().unwrap_or(0)
        }
    }

    pub fn node_count(&self) -> usize {
        1 + self.children.iter().map(|c| c.node_count()).sum::<usize>()
    }
}
