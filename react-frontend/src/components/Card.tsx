interface CardProps {
  children: React.ReactNode;
  className?: string;
}

function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`glass-card p-6 ${className}`}>
      {children}
    </div>
  );
}

export default Card;
