import React from 'react';
import { Users } from 'lucide-react';
import './CategorySelector.css';

const CategorySelector = ({ selectedCategory, onCategoryChange }) => {
  const categories = [
    { value: 'GOPEN', label: 'General Open', description: 'General Category - Open Merit' },
    { value: 'LOPEN', label: 'Ladies Open', description: 'Ladies - Open Merit' },
    { value: 'GOBCH', label: 'General OBC', description: 'General - Other Backward Class' },
    { value: 'LOBCH', label: 'Ladies OBC', description: 'Ladies - Other Backward Class' },
    { value: 'GSCH', label: 'General SC', description: 'General - Scheduled Caste' },
    { value: 'LSCH', label: 'Ladies SC', description: 'Ladies - Scheduled Caste' },
    { value: 'GSTH', label: 'General ST', description: 'General - Scheduled Tribe' },
    { value: 'GNT1H', label: 'General NT1', description: 'General - Nomadic Tribe 1' },
    { value: 'GNT2H', label: 'General NT2', description: 'General - Nomadic Tribe 2' },
    { value: 'GNT3H', label: 'General NT3', description: 'General - Nomadic Tribe 3' },
    { value: 'GVJH', label: 'General VJ', description: 'General - Vimukta Jati' }
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
