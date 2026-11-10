import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ConsentGroup, { formatRecordedDate } from '../components/onboarding/ConsentGroup';
import type { ConsentRecord } from '../types/consent';

const record: ConsentRecord = {
  id: 'x',
  purpose: 'personalized_insights',
  version: '1.0',
  status: 'declined',
  recorded_at: '2026-11-14T12:00:00Z',
};

function setup(rec?: ConsentRecord) {
  const onChoose = vi.fn();
  render(
    <ConsentGroup
      purpose="personalized_insights"
      title="Personalized insights"
      description="desc"
      meta="Purpose: personalized_insights."
      policyVersion="1.0"
      record={rec}
      onChoose={onChoose}
    />,
  );
  return onChoose;
}

describe('ConsentGroup', () => {
  it('shows the policy tag and no recorded line before a choice', () => {
    setup();
    expect(screen.getByRole('group', { name: 'Personalized insights' })).toBeInTheDocument();
    expect(screen.getByText('Policy v1.0')).toBeInTheDocument();
    expect(screen.queryByText(/Recorded/)).not.toBeInTheDocument();
  });

  it('reports Accept and Decline choices', async () => {
    const onChoose = setup();
    await userEvent.click(screen.getByLabelText('Accept'));
    await userEvent.click(screen.getByLabelText('Decline'));
    expect(onChoose).toHaveBeenNthCalledWith(1, 'accepted');
    expect(onChoose).toHaveBeenNthCalledWith(2, 'declined');
  });

  it('checks the recorded choice and shows its date and policy version', () => {
    setup(record);
    expect(screen.getByLabelText('Decline')).toBeChecked();
    expect(screen.getByLabelText('Accept')).not.toBeChecked();
    expect(
      screen.getByText(`Recorded ${formatRecordedDate(record.recorded_at)}, policy v1.0`),
    ).toBeInTheDocument();
  });
});
