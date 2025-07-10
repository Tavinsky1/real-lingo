import React from 'react';

interface ButtonProps {
    label: string;
    onClick: () => void;
    disabled?: boolean;
    style?: React.CSSProperties;
}

const Button: React.FC<ButtonProps> = ({ label, onClick, disabled = false, style }) => {
    return (
        <button onClick={onClick} disabled={disabled} style={style}>
            {label}
        </button>
    );
};

export default Button;