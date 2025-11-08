import React from 'react';
import { Users } from 'lucide-react';
import './CategorySelector.css';

const CategorySelector = ({ selectedCategory, onCategoryChange }) => {
  const categories = [
    { value: 'GOPEN', label: 'General Open', description: 'General Category - Open Merit' },
    { value: 'LOPEN', label: 'Ladies Open', description: 'Ladies - Open Merit' }
  ];

  return (
    <div className="category-selector">
      <div className="category-selector-header">
        <Users size={20} />
        <h3>Select Your Category</h3>
      </div>
      <p className="category-selector-description">
        Choose your admission category to get accurate predictions
      </p>

      <div className="category-grid">
        {categories.map((category) => (
          <button
            key={category.value}
            className={`category-option ${selectedCategory === category.value ? 'active' : ''}`}
            onClick={() => onCategoryChange(category.value)}
          >
            <div className="category-option-label">{category.label}</div>
            <div className="category-option-description">{category.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default CategorySelector;
