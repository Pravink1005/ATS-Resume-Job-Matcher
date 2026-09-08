from fastapi import APIRouter
router=APIRouter()
@router.get('/')
def root(): return {'service':'Resume-to-Job Matching Engine','version':'2.0.0','docs':'/docs'}
