import { render, screen } from '@testing-library/react';
import TrendChart from '../components/trends/TrendChart';

const points = [
  { observed_at: '2026-10-15T08:00:00Z', value: 70.1 },
  { observed_at: '2026-10-25T08:00:00Z', value: 69.5 },
  { observed_at: '2026-11-14T08:00:00Z', value: 68.4 },
];

describe('TrendChart', () => {
  it('renders an accessible line chart with a polyline, circles and an end-value label', () => {
    const { container } = render(<TrendChart points={points} metricLabel="Weight" unit="kg" />);
    const chart = screen.getByRole('img');
    expect(chart).toHaveAccessibleName(/Line chart of weight in kg/);
    expect(container.querySelectorAll('circle')).toHaveLength(3);
    const line = container.querySelector('polyline');
    expect(line).toHaveAttribute('stroke', '#6929c4');
    expect(line?.getAttribute('points')?.split(' ')).toHaveLength(3);
    expect(screen.getByText('68.4 kg')).toBeInTheDocument();
  });

  it('renders a single point without NaN coordinates', () => {
    const { container } = render(<TrendChart points={[points[0]]} metricLabel="Weight" unit="kg" />);
    expect(container.innerHTML).not.toContain('NaN');
  });

  it('renders nothing without points', () => {
    const { container } = render(<TrendChart points={[]} metricLabel="Weight" unit="kg" />);
    expect(container).toBeEmptyDOMElement();
  });
});
