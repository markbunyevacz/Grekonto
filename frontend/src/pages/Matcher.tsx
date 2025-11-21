  const handleDecision = async (decision: 'approve' | 'reject') => {
    if (!task) return;
    
    try {
      const newStatus = decision === 'approve' ? 'COMPLETED' : 'REJECTED';
      
      // Send status AND match_candidate if we have one
      const body: any = { status: newStatus };
      if (task.match_candidate) {
          body.match_candidate = task.match_candidate;
      }

      await fetch(`/api/tasks/${task.id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      navigate('/dashboard');
    } catch (error) {
      alert("Hiba történt a mentéskor.");
    }
  };
