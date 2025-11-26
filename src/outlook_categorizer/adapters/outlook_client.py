"""
Outlook COM interface adapter.
All Outlook-specific code is isolated here.
"""

import re
import logging
from datetime import datetime
from typing import Optional

from ..core.models import EmailMessage

logger = logging.getLogger(__name__)


def _strip_html(html: str) -> str:
    """Extract plain text from HTML content."""
    # Remove style and script blocks entirely
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Replace common block elements with newlines
    text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</(p|div|tr|li)>', '\n', text, flags=re.IGNORECASE)
    
    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Collapse multiple newlines
    text = re.sub(r'[ \t]+', ' ', text)       # Collapse spaces
    
    return text.strip()


class OutlookClient:
    """Interface to Outlook via COM."""
    
    def __init__(self):
        self._outlook = None
        self._namespace = None
        self._inbox = None
    
    def connect(self) -> bool:
        """
        Connect to Outlook.
        Returns True if successful, False otherwise.
        """
        try:
            import win32com.client
            
            self._outlook = win32com.client.Dispatch("Outlook.Application")
            self._namespace = self._outlook.GetNamespace("MAPI")
            
            # Get inbox folder (6 = olFolderInbox)
            self._inbox = self._namespace.GetDefaultFolder(6)
            
            logger.info(f"Connected to Outlook - Inbox: {self._inbox.Name}")
            return True
            
        except ImportError:
            logger.error("pywin32 not installed. Run: pip install pywin32")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Outlook: {e}")
            logger.error("Make sure Outlook is running and try again.")
            return False
    
    def is_connected(self) -> bool:
        """Check if Outlook connection is still valid."""
        try:
            # Try to access inbox name as a connection test
            _ = self._inbox.Name
            return True
        except:
            return False
    
    def get_emails_since(self, since: datetime) -> list[EmailMessage]:
        """
        Get all emails received since the given datetime.
        """
        emails = []
        
        if not self._inbox:
            logger.error("Not connected to Outlook")
            return emails
        
        try:
            # Format datetime for Outlook filter
            since_str = since.strftime("%m/%d/%Y %H:%M %p")
            filter_str = f"[ReceivedTime] >= '{since_str}'"
            
            items = self._inbox.Items
            items.Sort("[ReceivedTime]", Descending=True)
            filtered = items.Restrict(filter_str)
            
            for item in filtered:
                try:
                    email = self._extract_email(item)
                    if email:
                        emails.append(email)
                except Exception as e:
                    logger.warning(f"Failed to process email: {e}")
                    continue
            
            logger.debug(f"Found {len(emails)} emails since {since_str}")
            
        except Exception as e:
            logger.error(f"Error querying emails: {e}")
        
        return emails
    
    def _extract_email(self, item) -> Optional[EmailMessage]:
        """Extract email data from Outlook item."""
        try:
            # Skip non-mail items (meeting requests, etc.)
            if item.Class != 43:  # 43 = olMail
                return None
            
            # Get sender email
            sender_email = ""
            try:
                if item.SenderEmailType == "EX":
                    # Exchange address - get SMTP address
                    sender = item.Sender
                    if sender:
                        sender_email = sender.GetExchangeUser()
                        if sender_email:
                            sender_email = sender_email.PrimarySmtpAddress
                        else:
                            sender_email = item.SenderEmailAddress
                else:
                    sender_email = item.SenderEmailAddress
            except:
                sender_email = getattr(item, 'SenderEmailAddress', '')
            
            # Get attachment names
            attachment_names = []
            try:
                for att in item.Attachments:
                    attachment_names.append(att.FileName)
            except:
                pass
            
            # Get current categories
            categories = []
            try:
                if item.Categories:
                    categories = [c.strip() for c in item.Categories.split(",")]
            except:
                pass
            
            # Extract body text (check both plain and HTML, use best one)
            body = ""
            try:
                plain_body = (item.Body or "").strip()
                html_body = item.HTMLBody or ""
                
                # Extract text from HTML
                html_text = _strip_html(html_body) if html_body else ""
                
                # Use whichever has more content
                body = plain_body if len(plain_body) >= len(html_text) else html_text
            except Exception as e:
                logger.debug(f"Error extracting body: {e}")
                pass
            
            email = EmailMessage(
                entry_id=item.EntryID,
                subject=item.Subject or "",
                body=body,
                sender_email=sender_email or "",
                sender_name=getattr(item, 'SenderName', ''),
                received_time=datetime.fromtimestamp(item.ReceivedTime.timestamp()),
                attachment_names=attachment_names,
                categories=categories,
                conversation_id=getattr(item, 'ConversationID', ''),
            )
            # Set PrivateAttr after instantiation (can't be set in constructor)
            email._outlook_item = item
            return email
            
        except Exception as e:
            logger.warning(f"Error extracting email: {e}")
            return None
    
    def apply_category(self, email: EmailMessage, category: str) -> bool:
        """
        Apply a category to an email.
        Adds to existing categories (doesn't replace).
        """
        try:
            item = email._outlook_item
            if not item:
                logger.error("No Outlook item reference available")
                return False
            
            # Get current categories
            current = item.Categories or ""
            current_list = [c.strip() for c in current.split(",") if c.strip()]
            
            # Check if already has this category
            if category in current_list:
                logger.debug(f"Email already has category '{category}'")
                return True
            
            # Add new category
            current_list.append(category)
            item.Categories = ", ".join(current_list)
            item.Save()
            
            logger.info(f"Applied category '{category}' to: {email.subject[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply category: {e}")
            return False
    
    def get_available_categories(self) -> list[str]:
        """Get list of available categories in Outlook."""
        categories = []
        try:
            for cat in self._namespace.Categories:
                categories.append(cat.Name)
        except Exception as e:
            logger.warning(f"Could not retrieve categories: {e}")
        return categories

